from distutils import cmd, file_util, log
import subprocess

# This makes it possible to import from setup.py and
# get __version__ without having packaging installed
try:
    import packaging.version
except ImportError:  # pragma no cover
    pass


version_info = (1, 0, 1)
__version__ = '.'.join(str(v) for v in version_info)


class GitVersion(cmd.Command):
    description = 'Generate version numbers based on git'
    user_options = [
        ('version-file=', 'V', 'write the generated version to this file'),
    ]

    def initialize_options(self):
        self.version_file = None

    def finalize_options(self):  # pragma: no cover
        pass

    def run(self):
        version = packaging.version.parse(self.distribution.metadata.version)
        public_version, _ = _partition_version(version.public.split('.'))
        starting_rev = public_version

        local_version = []
        lines = self._run_git('rev-list', '--merges',
                              '{0}...HEAD'.format(starting_rev))
        self.debug('found {0} merges since tag {1}', len(lines), starting_rev)
        if lines:
            local_version.append('post{0}'.format(len(lines)))
            starting_rev = lines[0]

        lines = self._run_git('rev-list', '--first-parent',
                              '{0}...HEAD'.format(starting_rev))
        self.debug('found {0} commits since {1}', len(lines), starting_rev)
        if lines:
            local_version.append('dev{0}'.format(len(lines)))

        full_version = public_version
        if local_version:
            local_version = '.'.join(local_version)
            full_version += '.{0}'.format(local_version)
        self.info('setting version to {0}', full_version)
        self.distribution.metadata.version = full_version

        if self.version_file is not None:
            version_lines = []
            if local_version:
                version_lines.append('.' + local_version)
            self.debug('writing local version {0} to {1}',
                       local_version, self.version_file)
            if not self.dry_run:
                file_util.write_file(self.version_file, version_lines)

    def info(self, message, *args):
        self.announce(message.format(*args), level=log.INFO)

    def debug(self, message, *args):
        self.announce(message.format(*args), level=log.DEBUG)

    def _run_git(self, *args):
        if self.dry_run:
            self.debug('{0} {1}', 'git', ' '.join(args))
            return ['']
        stdout, stderr = _run_command('git', *args)
        if stderr:  # pragma: no cover
            self.debug('{0} {1} produced output on stderr: {2}',
                       'git', ' '.join(args), stderr)
        return stdout.splitlines()


def _run_command(git_program, *args):
    exec_list = [git_program]
    exec_list.extend(args)
    pipe = subprocess.Popen(exec_list,
                            close_fds=True,
                            universal_newlines=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = pipe.communicate()
    if pipe.returncode != 0:
        raise subprocess.CalledProcessError(pipe.returncode,
                                            ' '.join(exec_list))
    return stdout, stderr


def _partition_version(segments):
    """Partition a version list into public and local parts."""
    needle = len(segments)
    for index, segment in enumerate(segments):
        try:
            int(segment)
        except ValueError:
            needle = index
            break
    return '.'.join(segments[:needle]), '.'.join(segments[needle:])
