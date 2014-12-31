from distutils import cmd, log
import subprocess

# This makes it possible to import from setup.py and
# get __version__ without having packaging installed
try:
    import packaging.version
except ImportError:
    pass


version_info = (0, 0, 0)
__version__ = '.'.join(str(v) for v in version_info)


class GitVersion(cmd.Command):
    description = 'Generate version numbers based on git'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        version = packaging.version.parse(self.distribution.metadata.version)

        version_info = {'release': []}
        segments = version.public.split('.')
        while segments:
            try:
                version_info['release'].append(int(segments[0]))
                segments.pop(0)
            except ValueError:
                break
        version_info['release'] = '.'.join(
            str(v) for v in version_info['release'])

        rev_spec = '{0}...HEAD'.format(version_info['release'])

        lines = self._run_git('rev-list', '--merges', rev_spec)
        self.debug('found {0} merges since tag {1}',
                   len(lines), version_info['release'])
        version_info['post'] = len(lines)

        try:
            rev_spec = '{0}...HEAD'.format(lines.pop(0))
        except IndexError:
            pass
        lines = self._run_git('rev-list', '--first-parent', rev_spec)
        version_info['dev'] = len(lines)

        version = '{0}.post{1}.dev{2}'.format(
            version_info['release'],
            version_info['post'],
            version_info['dev'],
        )
        self.info('setting version to {0}', version)
        self.distribution.metadata.version = version

    def info(self, message, *args):
        self.announce(message.format(*args), level=log.INFO)

    def debug(self, message, *args):
        self.announce(message.format(*args), level=log.DEBUG)

    def _run_git(self, *args):
        if self.dry_run:
            self.debug('{0} {1}', 'git', ' '.join(args))
            return ['']
        stdout, stderr = _run_command('git', *args)
        if stderr:
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
