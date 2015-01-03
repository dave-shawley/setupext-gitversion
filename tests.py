from distutils import dist
import os.path
import shutil
import tempfile
import unittest

try:
    from unittest import mock
except ImportError:
    import mock

from setupext import gitversion


UNSPECIFIED = object()


class ProgrammableCallable(object):
    """
    Intelligent callable mock.

    This class implements a more complex mock of a callable.  Use this
    when you need to stub something that is called multiple times and
    has different response based on the argument list.

    """

    def __init__(self, default_value=None):
        self.return_values = {}
        self.calls = set()
        self.default_value = default_value or mock.Mock()

    def __call__(self, *args, **kwargs):
        call_signature = tuple(args)
        self.calls.add(call_signature)
        if call_signature in self.return_values:
            return self.return_values[call_signature]
        return self.default_value

    def add_return_value(self, return_value, *args, **kwargs):
        self.return_values[tuple(args)] = return_value

    def assert_called(self, *args):
        if tuple(args) not in self.calls:
            raise AssertionError(
                'expected {0} in {1}'.format(args, self.calls))


class WhenInitializingOptions(unittest.TestCase):

    def setUp(self):
        super(WhenInitializingOptions, self).setUp()
        self.distribution = dist.Distribution()
        self.command = gitversion.GitVersion(self.distribution)
        self.command.initialize_options()

    def test_that_default_is_defined_for_each_option(self):
        for long_opt, short_opt, desc in gitversion.GitVersion.user_options:
            attr_name = long_opt.replace('-', '_').rstrip('=')
            attr_value = getattr(self.command, attr_name, UNSPECIFIED)
            self.assertNotEqual(attr_value, UNSPECIFIED)


class CommandTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(CommandTestCase, cls).setUpClass()
        cls.distribution = dist.Distribution(attrs={'version': '1.2.3'})
        cls.run_git_command = ProgrammableCallable()
        cls.configure(cls.run_git_command)

        with mock.patch('setupext.gitversion._run_command',
                        new=cls.run_git_command):
            command = gitversion.GitVersion(cls.distribution)
            command.initialize_options()
            cls.execute(command)

    @classmethod
    def configure(cls, git_cmd):
        raise NotImplementedError

    @classmethod
    def execute(cls, command):
        raise NotImplementedError


class WhenRunningCommand(CommandTestCase):
    @classmethod
    def configure(cls, git_cmd):
        git_cmd.add_return_value(
            ('second merge\nfirst merge\n', ''),
            'git', 'rev-list', '--merges', '1.2.3...HEAD',
        )
        git_cmd.add_return_value(
            ('third commit\nsecond commit\nfirst commit\n', ''),
            'git', 'rev-list', '--first-parent', 'second merge...HEAD',
        )

    @classmethod
    def execute(cls, command):
        command.run()

    def test_that_git_is_called_for_merges(self):
        self.run_git_command.assert_called(
            'git', 'rev-list', '--merges', '1.2.3...HEAD')

    def test_that_git_is_called_for_commits_since_merge(self):
        self.run_git_command.assert_called(
            'git', 'rev-list', '--first-parent', 'second merge...HEAD')

    def test_that_version_is_set_correctly(self):
        self.assertEqual(
            self.distribution.metadata.version, '1.2.3.post2.dev3')


class WhenGeneratingVersionFile(CommandTestCase):
    @classmethod
    def configure(cls, git_cmd):
        git_cmd.add_return_value(
            ('1\n', ''),
            'git', 'rev-list', '--merges', '1.2.3...HEAD',
        )
        git_cmd.add_return_value(
            ('1.2\n1.1\n', ''),
            'git', 'rev-list', '--first-parent', '1...HEAD',
        )
        cls._tmp_dir = tempfile.mkdtemp()
        cls.version_file = os.path.join(cls._tmp_dir, 'VERSION-INFO')

    @classmethod
    def tearDownClass(cls):
        super(WhenGeneratingVersionFile, cls).tearDownClass()
        shutil.rmtree(cls._tmp_dir)

    @classmethod
    def execute(cls, command):
        command.version_file = cls.version_file
        command.run()

    def test_that_version_is_set_correctly(self):
        self.assertEqual(
            self.distribution.metadata.version, '1.2.3.post1.dev2')

    def test_that_version_file_was_created(self):
        self.assertTrue(os.path.exists(self.version_file))

    def test_that_version_file_contains_local_version(self):
        with open(self.version_file) as version_file:
            self.assertEqual(
                version_file.readlines(),
                ['.post1.dev2\n'],
            )


class WhenGeneratingVersionFileFromReleaseVersion(CommandTestCase):
    @classmethod
    def configure(cls, git_cmd):
        git_cmd.add_return_value(
            ('', ''),
            'git', 'rev-list', '--merges', '1.2.3...HEAD',
        )
        git_cmd.add_return_value(
            ('', ''),
            'git', 'rev-list', '--first-parent', '1.2.3...HEAD',
        )
        cls._tmp_dir = tempfile.mkdtemp()
        cls.version_file = os.path.join(cls._tmp_dir, 'VERSION-INFO')

    @classmethod
    def tearDownClass(cls):
        super(WhenGeneratingVersionFileFromReleaseVersion, cls).tearDownClass()
        shutil.rmtree(cls._tmp_dir)

    @classmethod
    def execute(cls, command):
        command.version_file = cls.version_file
        command.run()

    def test_that_version_is_set_correctly(self):
        self.assertEqual(self.distribution.metadata.version, '1.2.3')

    def test_that_version_file_is_empty(self):
        with open(self.version_file) as version_file:
            self.assertEqual(version_file.readlines(), [])


class WhenRunningInDryRunMode(CommandTestCase):

    @classmethod
    def configure(cls, git_cmd):
        cls.version_file = tempfile.mktemp()

    @classmethod
    def execute(cls, command):
        command.version_file = cls.version_file
        command._dry_run = True
        command.run()

    def test_that_command_is_not_run(self):
        self.assertEqual(list(self.run_git_command.calls), [])

    def test_that_version_file_is_not_created(self):
        self.assertFalse(os.path.exists(self.version_file))


class _RunCommandTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(_RunCommandTestCase, cls).setUpClass()
        with mock.patch('setupext.gitversion.subprocess') as subprocess:
            cls.subprocess_module = subprocess
            subprocess.CalledProcessError = Exception
            cls.configure(subprocess.Popen)
            try:
                cls.execute()
            except subprocess.CalledProcessError as exc:
                cls.exception = exc

    @classmethod
    def configure(cls, popen):
        cls.exception = None
        cls.popen = popen
        cls.pipe = cls.popen.return_value
        cls.pipe.communicate.return_value = (
            mock.sentinel.out, mock.sentinel.err)

    @classmethod
    def execute(cls):
        cls.returned = gitversion._run_command(
            mock.sentinel.git, mock.sentinel.arg1, mock.sentinel.arg2)

    def test_that_pipe_is_opened_to_correct_command(self):
        self.popen.assert_called_once_with(
            [mock.sentinel.git, mock.sentinel.arg1, mock.sentinel.arg2],
            close_fds=True, universal_newlines=True,
            stdout=self.subprocess_module.PIPE,
            stderr=self.subprocess_module.PIPE,
        )


class WhenInternallyRunningCommand(_RunCommandTestCase):

    @classmethod
    def configure(cls, popen):
        super(WhenInternallyRunningCommand, cls).configure(popen)
        cls.pipe.returncode = 0

    def test_that_pipe_communication_invoked(self):
        self.pipe.communicate.assert_called_once_with()

    def test_that_no_exception_is_raised(self):
        self.assertIsNone(self.exception)

    def test_that_output_is_returned(self):
        self.assertEqual(self.returned, self.pipe.communicate.return_value)


class WhenInternallyRunningCommandThatFails(_RunCommandTestCase):

    @classmethod
    def configure(cls, popen):
        super(WhenInternallyRunningCommandThatFails, cls).configure(popen)
        cls.pipe.returncode = 2

    def test_that_called_process_error_is_raised(self):
        self.assertIsInstance(
            self.exception, self.subprocess_module.CalledProcessError)
