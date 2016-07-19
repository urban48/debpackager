import os
import shutil
import tempfile

from sh import mkdir
import pytest

from debpackager.utils.pom import Pom
from debpackager.utils import general
import debpackager.packages.conf.configurations as cfg


@pytest.mark.unit
class TestUtilsGeneral(object):
    def setup_method(self, method):
        self.tmp_dir = tempfile.mkdtemp()

        mkdir(self.tmp_dir + '/' + 'folderA').wait()
        mkdir(self.tmp_dir + '/' + 'folderB').wait()
        mkdir(self.tmp_dir + '/' + 'debian').wait()
        with open(self.tmp_dir + '/' + 'project.json', 'w') as f:
            project_conf = '''{
                  "version": "0.1.0",
                  "type": "general",
                  "debians": [{"name":"test-proj", "install_path": "/opt/test-proj"}],
                  "deb_dependencies" : []
                }
                '''
            f.write(project_conf)
        self.pom = Pom(project_path=self.tmp_dir)
        os.chdir(self.tmp_dir)

    def teardown_method(self, method):
        shutil.rmtree(self.tmp_dir)

    def test_get_new_version(self):
        version = general.get_new_version({'pom': self.pom})
        assert version == '0.1.0'

    def test_get_new_version_not_semver(self):
        self.pom.project['version'] = '1.1'
        with pytest.raises(Exception):
            general.get_new_version({'pom': self.pom})

    def test_get_new_version_missing_version_field(self):
        del self.pom.project['version']
        with pytest.raises(Exception):
            general.get_new_version({'pom': self.pom})

    def test_get_new_version_custom_version(self):
        version = general.get_new_version({'pom': self.pom,
                                           'custom_version': '2.2.2'})
        assert version == '2.2.2'

    def test_get_new_version_invalid_custom_version(self):
        with pytest.raises(Exception):
            general.get_new_version({'pom': self.pom,
                                     'custom_version': '2.2'})

    def test_create_virtual_env_path(self):
        ve_path = general.create_virtual_env(self.tmp_dir, '/tmp/install_path')
        assert ve_path == self.tmp_dir + '/' + cfg.VIRTUAL_ENV_PATH
        shutil.rmtree(ve_path)

    def test_create_virtual_env_requirements(self):
        with open(self.tmp_dir + '/' + 'requirements.txt', 'w') as f:
            f.write('pytest')
        ve_path = general.create_virtual_env(self.tmp_dir, '/tmp/install_path')
        assert os.path.exists('{}/bin/py.test'.format(ve_path)) == True
        shutil.rmtree(ve_path)

    def test_fixup_scripts(self):
        with open(self.tmp_dir + '/' + 'requirements.txt', 'w') as f:
            f.write('pytest')
        general.create_virtual_env(self.tmp_dir, '/tmp/install_path')
        with open(self.tmp_dir + '/ve/bin/py.test', 'rb') as f:
            lines = f.read().decode('utf-8').splitlines()
            lines[0].strip()
        assert lines[0].strip() \
                   .startswith('#!/tmp/install_path/ve/bin') == True
