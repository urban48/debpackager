import logging
import os


from debpackager.utils.debain_package_manager import Dpm
from debpackager.utils.general import get_new_version
from debpackager.packages.conf import configurations as cfg
from debpackager.conf import configuratoin as global_cfg


logger = logging.getLogger(__name__)


class GeneralPackage(object):
    def __init__(self, **kwargs):

        self.extra_args = kwargs
        if kwargs.get('action') == 'build':
            self.validate_project()

        self.project_path = kwargs.get('project_path')
        self.project_name = kwargs.get('project_name')
        self.new_version = None
        self.extra_files = []
        self.path_to_debians = os.path.join(self.project_path,
                                            cfg.PACKAGE_ROOT)

    def validate_project(self):
        """ Insures project file has all the mandatory fields for a specific
        project type

        """
        project = getattr(self.extra_args.get('pom'), 'project')
        if not project:
            return
        mandatory_fields = ['version', 'debians', 'type']
        diffs = set(mandatory_fields) - set(project.keys())
        if diffs:
            raise Exception(
                'The following mandatory fields: {}\nare missing from '
                'project.json'.format(
                    ', '.join(diffs)))

        debians = project.get('debians')
        if not isinstance(debians, list) or len(debians) == 0:
            raise Exception(
                'Debians array in project.json is empty, it must contain '
                'at least on debian')

        for deb in debians:
            if not deb:
                raise Exception(
                    'Objects in debians array in project.json cannot be '
                    'empty, it must contain information about the debian')
            if "install_path" not in deb:
                raise Exception(
                    "Objects in debians array in project.json must contain "
                    "'install_path' field")
            if "name" not in deb:
                raise Exception('Objects in debians array in project. json '
                                'must contain "name" field')

    def build(self):
        """ builds debian package

        """
        self.new_version = get_new_version(self.extra_args)
        generated_builds = ['{}/{}'.format(self.project_path, build) for
                            build in os.listdir(self.project_path) if
                            build.startswith(global_cfg.BUILD_DEBIAN_DIR)]
        if not generated_builds:
            generated_builds = self.generate()
        for build in generated_builds:
            Dpm.build(build)

        # leftovers after debian creation
        # will be deleted if --no-clean flag is given
        self.extra_files.extend(['*.tar.gz', '*.tar.xz', '*amd64.changes',
                                '*.dsc'])
        self.extra_files.extend(generated_builds)

    def generate(self):
        self.new_version = get_new_version(self.extra_args)

        deb_dependencies = self.extra_args.get('pom', {}) \
            .project.get('deb_dependencies')
        project = self.extra_args.get('pom', {}).project
        generated_builds = []
        for deb in project.get('debians', []):
            deb_name = deb.get('name', self.project_name)
            dpm = Dpm(project_path=self.project_path,
                      package_name=deb_name,
                      package_version=self.new_version,
                      install_path=deb.get('install_path'),
                      dependencies=deb_dependencies,
                      description=deb.get('description'),
                      excludes=project.get('excludes', []))

            generated_builds.append(dpm.generate())
        return generated_builds
