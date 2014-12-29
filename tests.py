from distutils import dist
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


class WhenRunningCommand(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(WhenRunningCommand, cls).setUpClass()
        cls.distribution = dist.Distribution(attrs={'version': '1.2.3'})
        cls.run_git_command = ProgrammableCallable()
        cls.run_git_command.add_return_value(
            ('second merge\nfirst merge\n', ''),
            'git', 'rev-list', '--merges', '1.2.3...HEAD',
        )
        cls.run_git_command.add_return_value(
            ('third commit\nsecond commit\nfirst commit\n', ''),
            'git', 'rev-list', '--first-parent', 'second merge...HEAD',
        )

        with mock.patch('setupext.gitversion._run_command',
                        new=cls.run_git_command):
            cls.command = gitversion.GitVersion(cls.distribution)
            cls.command.initialize_options()
            cls.command.run()

    def test_that_git_is_called_for_merges(self):
        self.run_git_command.assert_called(
            'git', 'rev-list', '--merges', '1.2.3...HEAD')

    def test_that_git_is_called_for_commits_since_merge(self):
        self.run_git_command.assert_called(
            'git', 'rev-list', '--first-parent', 'second merge...HEAD')

    def test_that_version_is_set_correctly(self):
        self.assertEqual(
            self.command.distribution.metadata.version, '1.2.3.post2.dev3')
