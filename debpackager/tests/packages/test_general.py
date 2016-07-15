import json
import os
import tempfile

from sh import mkdir
import pytest

from debpackager.utils.pom import Pom
from debpackager.packages.general.general import General


@pytest.mark.unitest
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
                  "deb_dependencies" : [],
                  "excludes" : []
                }
                '''
            f.write(project_conf)
        self.pom = Pom(project_path=self.tmp_dir)
        os.chdir(self.tmp_dir)

    def test_build(self):
        gp = General({'project_path': self.tmp_dir,
                      'project_type': 'general',
                      'pom': self.pom})
        gp.build()
        assert os.path.exists(self.tmp_dir +
                              '/test-proj_0.1.0_all.deb') == True

    def test_build_with_dependencies(self):
        with open(self.tmp_dir + '/' + 'project.json', 'r') as pjf:
            j = json.loads(pjf.read())
            j['deb_dependencies'].append('python-pip>=1.5.4-1')
            with open(self.tmp_dir + '/' + 'project.json', 'w') as tkw:
                tkw.write(json.dumps(j))

        pom = Pom(project_path=self.tmp_dir)
        gp = General({'project_path': self.tmp_dir,
                      'project_type': 'general',
                      'pom': pom})
        gp.build()
        result = os.popen('dpkg -I test-proj_0.1.0_all.deb').read()
        assert 'Depends: python-pip (>= 1.5.4-1)' in result

    def test_build_with_exclude(self):
        with open(self.tmp_dir + '/' + 'project.json', 'r') as pjf:
            j = json.loads(pjf.read())
            j['excludes'].append('folderB')
            with open(self.tmp_dir + '/' + 'project.json', 'w') as tkw:
                tkw.write(json.dumps(j))

        pom = Pom(project_path=self.tmp_dir)
        gp = General({'project_path': self.tmp_dir,
                      'project_type': 'general',
                      'pom': pom})
        gp.build()
        result = os.popen('dpkg -c test-proj_0.1.0_all.deb').read()
        assert 'folderA' in result
        assert 'folderB' not in result

    def test_build_with_description(self):
        with open(self.tmp_dir + '/' + 'project.json', 'r') as pjf:
            j = json.loads(pjf.read())
            j['debians'][0]['description'] = 'test description package'
            with open(self.tmp_dir + '/' + 'project.json', 'w') as tkw:
                tkw.write(json.dumps(j))

        pom = Pom(project_path=self.tmp_dir)
        gp = General({'project_path': self.tmp_dir,
                      'project_type': 'general',
                      'pom': pom})
        gp.build()
        result = os.popen('dpkg -I test-proj_0.1.0_all.deb').read()
        assert 'Description: test description package' in result

    def test_build_without_description(self):
        pom = Pom(project_path=self.tmp_dir)
        gp = General({'project_path': self.tmp_dir,
                      'project_type': 'general',
                      'pom': pom})
        gp.build()
        result = os.popen('dpkg -I test-proj_0.1.0_all.deb').read()
        assert 'Description: test-proj Package' in result

    def test_build_with_long_description(self):
        with open(self.tmp_dir + '/' + 'project.json', 'r') as pjf:
            j = json.loads(pjf.read())
            j['debians'][0]['description'] = 'test description package' * 100
            with open(self.tmp_dir + '/' + 'project.json', 'w') as tkw:
                tkw.write(json.dumps(j))

        pom = Pom(project_path=self.tmp_dir)
        gp = General({'project_path': self.tmp_dir,
                      'project_type': 'general',
                      'pom': pom})
        gp.build()
        result = os.popen('dpkg -I test-proj_0.1.0_all.deb').read()
        assert 'Description: test-proj Package' in result