import json
import os
import shutil
import tempfile
import logging
from debpackager.utils.pom import Pom

from sh import mkdir
import pytest

from debpackager.main import get_project_type, add_missing_params

logging.basicConfig(level=logging.WARNING)


@pytest.mark.unit
class TestMain(object):

    def setup_method(self, method):

        self.tmp_dir = tempfile.mkdtemp()

        mkdir(self.tmp_dir + '/' + 'folderA').wait()
        mkdir(self.tmp_dir + '/' + 'folderB').wait()
        mkdir(self.tmp_dir + '/' + 'debian').wait()
        with open(self.tmp_dir + '/' + 'project.json', 'w') as proj_file:
            project_conf = '''{
                  "version": "0.1.0",
                  "type": "python",
                  "debians": [{"name":"test-proj", "install_path": "/opt/test-proj"}],
                  "deb_dependencies" : [],
                  "excludes" : []
                }
                '''
            proj_file.write(project_conf)

    def teardown_method(self, method):
        shutil.rmtree(self.tmp_dir)

    def test_get_project_type_python(self):
        with open(self.tmp_dir + '/' + 'requirements.txt', 'w') as req_file:
            req_file.write('something')
        assert get_project_type(self.tmp_dir) == 'python'

    def test_get_project_type_general(self):
        assert get_project_type(self.tmp_dir) == 'general'

    def test_get_project_type_wrong_path(self):
        with pytest.raises(Exception) as excinfo:
            get_project_type('/bad/path')

        assert str(excinfo.value) == 'Could not find project path: /bad/path'

    def test_add_missing_params_with_project_name(self):
        with open(self.tmp_dir + '/' + 'project.json', 'r+') as proj_file:
            proj = json.loads(proj_file.read())
            proj['name'] = 'test_proj_name'
            proj_file.seek(0)
            proj_file.write(json.dumps(proj))
            proj_file.truncate()

        pom = Pom(project_path=self.tmp_dir)
        os.chdir(self.tmp_dir)
        args = DotDict()
        args['project_path'] = os.getcwd()
        args['project_type'] = None
        result = add_missing_params(args, pom)
        assert result.project_name == 'test_proj_name'

    def test_add_missing_params_no_project_name(self):
        pom = Pom(project_path=self.tmp_dir)
        os.chdir(self.tmp_dir)
        args = DotDict()
        args['project_path'] = os.getcwd()
        args['project_type'] = None
        result = add_missing_params(args, pom)
        assert result.project_name == os.path.basename(self.tmp_dir)

    def test_add_missing_params_with_project_type(self):

        pom = Pom(project_path=self.tmp_dir)
        os.chdir(self.tmp_dir)
        args = DotDict()
        args['project_path'] = os.getcwd()
        args['project_type'] = None
        result = add_missing_params(args, pom)
        assert result.project_type == 'general'

    def test_add_missing_params_no_project_type_general(self):
        with open(self.tmp_dir + '/' + 'project.json', 'r+') as proj_file:
            proj = json.loads(proj_file.read())
            del proj['type']
            proj_file.seek(0)
            proj_file.write(json.dumps(proj))
            proj_file.truncate()

        pom = Pom(project_path=self.tmp_dir)
        os.chdir(self.tmp_dir)
        args = DotDict()
        args['project_path'] = os.getcwd()
        args['project_type'] = None
        result = add_missing_params(args, pom)
        assert result.project_type == 'general'

    def test_add_missing_params_no_project_type_python(self):
        with open(self.tmp_dir + '/' + 'project.json', 'r+') as proj_file:
            proj = json.loads(proj_file.read())
            del proj['type']
            proj_file.seek(0)
            proj_file.write(json.dumps(proj))
            proj_file.truncate()
        with open(self.tmp_dir + '/' + 'requirements.txt', 'w') as req_file:
            req_file.write('something')

        pom = Pom(project_path=self.tmp_dir)
        os.chdir(self.tmp_dir)
        args = DotDict()
        args['project_path'] = os.getcwd()
        args['project_type'] = None
        result = add_missing_params(args, pom)
        assert result.project_type == 'python'


class DotDict(dict):
    def __getattr__(self, name):
        return self[name]
