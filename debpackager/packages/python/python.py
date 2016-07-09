from debpackager.packages.general_package import GeneralPackage
from debpackager.utils.general import create_virtual_env, \
    install_deb_dependencies

import debpackager.packages.conf.configurations as cfg


class Python(GeneralPackage):
    def __init__(self, kwargs):
        super(Python, self).__init__(**kwargs)
        self.install_debians = kwargs.get('install_dependencies')

    def build(self):
        if self.install_debians:
            install_deb_dependencies(self.extra_args)

        for debian in self.extra_args.get('pom').project.get('debians', []):
            install_path = debian.get('install_path')
            create_virtual_env(self.project_path, install_path)
            super(Python, self).build()

            # virtualenv dir will be deleted if --no-clean flag is given
            self.extra_files.append(cfg.VIRTUAL_ENV_PATH)

        super(Python, self).build()
