from distutils import cmd


version_info = (0, 0, 0)
__version__ = '.'.join(str(v) for v in version_info)


class GitVersion(cmd.Command):
    description = 'Generate version numbers based on git'

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        pass
