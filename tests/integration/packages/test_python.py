import json
import os
import tempfile
import shutil
import subprocess

import pytest

from debpackager.utils.pom import Pom
import debpackager.packages.conf.configurations as cfg
from debpackager.packages.python.python import Python


@pytest.mark.integration
class TestPython(object):

    def setup_method(self, method):
        self.tmp_dir = tempfile.mkdtemp()

        os.makedirs(self.tmp_dir + '/' + 'folderA')
        os.makedirs(self.tmp_dir + '/' + 'folderB')
        with open(self.tmp_dir + '/' + 'project.json', 'w') as f:
            project_conf = '''{
                  "version": "0.1.0",
                  "type": "python",
                  "debians": [{"name":"test-proj",
                               "install_path": "/opt/test-proj"}],
                  "deb_dependencies" : [],
                  "excludes" : []
                }
                '''
            f.write(project_conf)

        os.chdir(self.tmp_dir)

    def teardown_method(self, method):
        shutil.rmtree(self.tmp_dir)

    def test_build_no_requirements(self):
        pp = Python({'project_path': self.tmp_dir,
                     'pom': Pom(project_path=self.tmp_dir)})
        pp.build()
        assert os.path.exists(self.tmp_dir +
                              '/test-proj_0.1.0_all.deb') == True
        cmd = 'dpkg -c {}/test-proj_0.1.0_all.deb'.format(self.tmp_dir)
        result = subprocess.check_output(cmd, shell=True)
        deb_ve_install_path = os.path.join(pp.extra_args['pom']
                                           .project['debians'][0]
                                           ['install_path'],
                                           cfg.VIRTUAL_ENV_PATH)

        assert deb_ve_install_path in result

    def test_build_with_custom_interpreter27(self):
        with open(self.tmp_dir + '/' + 'project.json', 'r') as pjf:
            j = json.loads(pjf.read())
            j['debians'][0]['ve_args'] = ['-p', 'python2.7']
            with open(self.tmp_dir + '/' + 'project.json', 'w') as tkw:
                tkw.write(json.dumps(j))

        pp = Python({'project_path': self.tmp_dir,
                     'pom': Pom(project_path=self.tmp_dir)})

        pp.build()
        cmd = 'dpkg -c {}/test-proj_0.1.0_all.deb'.format(self.tmp_dir)
        result = subprocess.check_output(cmd, shell=True)
        assert '/ve/bin/python2.7' in result
