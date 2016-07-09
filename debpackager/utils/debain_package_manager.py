import os
import re
import shutil
import logging

import sh

from debpackager.utils.general import run_command

import debpackager.conf.configuratoin as cfg

logger = logging.getLogger(__name__)


class Dpm(object):
    """ class for creating and editing debian setup files """

    def __init__(self, project_path,
                 package_name,
                 package_version,
                 install_path,
                 dependencies=None,
                 excludes=None):

        self.project_path = project_path
        self.package_name = package_name
        self.package_version = package_version
        self.install_path = install_path
        self.dependencies = dependencies
        self.excludes = excludes or []
        self.deb_setting_dir = os.path.join(self.project_path,
                                            cfg.PROJECT_DEBIAN_SETTINGS_DIR)
        self.debian_package_path = os.path.join(project_path,
                                                cfg.BUILD_DEBIAN_DIR)
        if os.path.exists(self.debian_package_path):
            shutil.rmtree(self.debian_package_path)
        os.mkdir(self.debian_package_path)
        os.chdir(self.debian_package_path)

    def build(self):
        """ builds debian packages"""
        self._dh_make()
        self._create_install_file()
        self._add_deb_dependencies()
        self._set_exclude()
        self._add_maintainer_scripts()
        self._add_startup_script()
        run_command('dpkg-buildpackage -uc -us -tc -rfakeroot')
        os.chdir(self.project_path)

        return cfg.BUILD_DEBIAN_DIR

    def _dh_make(self):
        """ creates a debian subdirectory with initial files that are needed
         to create .deb package
        """
        return run_command(['dh_make',
                            '-C',
                            'i',
                            '-y',
                            '--native',
                            '-p',
                            self.package_name + '_' + self.package_version])

    def _create_install_file(self):
        """ sets files that need to be installed and configures the install
        destination of your package,
        by default will include all of the root directory

        """
        source_path = os.path.join('../../',
                                   os.path.basename(self.project_path),
                                   '*')

        with open('debian/{}.install'.format(self.package_name),
                  'w') as inst_f:
            inst_f.write('{} {}\n'.format(source_path, self.install_path))

    def _add_deb_dependencies(self):
        """ adds deb dependencies to control file """
        if self.dependencies:
            debian_dependencies = self._dependencies_to_debian_format(
                self.dependencies)
            dependencies_str = ', '.join(debian_dependencies)

            sh.sed('-i', r'/^Depends/c\\Depends: ${{misc:Depends}}, {}'
                   .format(dependencies_str),
                   self.debian_package_path + '/debian/control').wait()

    def _set_exclude(self):
        """ add excludes to rules files"""
        self.excludes += cfg.DEBIAN_EXCLUDES
        if self.excludes:
            excludes_str = ' '.join(['-X ' + e for e in self.excludes])
            excludes_str += ' -X {}'.format(cfg.BUILD_DEBIAN_DIR)
            excludes_str += ' -X {}'.format(cfg.PROJECT_DEBIAN_SETTINGS_DIR)
            with open(self.debian_package_path + '/debian/rules', 'a') as \
                    rule_f:
                rule_f.write('\tdh_install ' + excludes_str + '\n')

    def _add_maintainer_scripts(self):
        """ creates maintainer scrips if they exist at debian/ dir at the
        project
        """
        if not os.path.exists(self.deb_setting_dir):
            return
        # get all custom maintainer scripts, files that don't have '.' in name
        mscripts = list(filter(lambda x: '.' not in x, os.listdir(
            self.deb_setting_dir)))

        # copy to appropriate location
        for script in mscripts:
            shutil.copy(os.path.join(self.deb_setting_dir, script),
                        os.path.join(self.debian_package_path,
                                     'debian',
                                     self.package_name + '.' + script))

    def _add_startup_script(self):
        """ adds startup scrip if they exists in debian/ dir in the project.
        currently supports upstart, and SysVinit

        """
        if not os.path.exists(self.deb_setting_dir):
            return

        upstart = list(filter(lambda x: '.upstart' in x, os.listdir(
            self.deb_setting_dir)))
        if upstart:
            shutil.copy(os.path.join(self.deb_setting_dir, upstart[0]),
                        os.path.join(self.debian_package_path,
                                     'debian',
                                     upstart[0]))
            return

        initd = list(filter(lambda x: '.init' in x, os.listdir(
            self.deb_setting_dir)))
        if initd:
            shutil.copy(os.path.join(self.deb_setting_dir, initd[0]),
                        os.path.join(self.debian_package_path,
                                     'debian',
                                     initd[0]))
            return
        logger.warning('No start-up scrip was found')

    @staticmethod
    def _dependencies_to_debian_format(dependencies):
        """ reformat deb dependencies to format that debian can understand"""
        debian_dependencies = []
        for deb_name in dependencies:
            m = re.match(r'([^\s<>=]+)([<>=]{1,2})([^\s<>=]+)', deb_name)
            if m:
                debian_dependencies.append('{}({}{})'.format(*m.groups()))
            else:
                debian_dependencies.append(deb_name)
        return debian_dependencies
