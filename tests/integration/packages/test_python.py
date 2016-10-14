import os
import tempfile

import pytest
import sh

from debpackager.utils.pom import Pom
from debpackager.packages.python.python import Python


@pytest.mark.integration
class TestPython():

    def setup_method(self, method):
        self.tmp_dir = tempfile.mkdtemp()

        sh.mkdir(self.tmp_dir + '/' + 'folderA').wait()
        sh.mkdir(self.tmp_dir + '/' + 'folderB').wait()
        with open(self.tmp_dir + '/' + 'project.json', 'w') as f:
            project_conf = '''{
                  "version": "0.1.0",
                  "type": "python",
                  "debians": [{"name":"test-proj", "install_path": "/opt/test-proj"}],
                  "deb_dependencies" : [],
                  "excludes" : []
                }
                '''
            f.write(project_conf)
        self.pom = Pom(project_path=self.tmp_dir)
        os.chdir(self.tmp_dir)

    def test_build_no_requirements(self):
        pp = Python({'project_path': self.tmp_dir,
                     'project_type': 'general',
                     'pom': self.pom})
        pp.build()
        assert os.path.exists(self.tmp_dir +
                              '/test-proj_0.1.0_all.deb') == True
        result = os.popen('dpkg -c test-proj_0.1.0_all.deb').read()
        print(result)