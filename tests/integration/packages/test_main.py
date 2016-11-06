import glob
import os
import sys
import tempfile
import shutil

import pytest

from debpackager import main


@pytest.mark.integration
class TestMain(object):

    def setup_method(self, method):
        self.tmp_dir = tempfile.mkdtemp()

        os.makedirs(self.tmp_dir + '/' + 'folderA')
        os.makedirs(self.tmp_dir + '/' + 'folderB')
        os.makedirs(self.tmp_dir + '/' + 'debian')
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
        os.chdir(self.tmp_dir)

    def teardown_method(self, method):
        shutil.rmtree(self.tmp_dir)

    def test_generate(self):
        sys.argv = ['', 'generate', '-p', self.tmp_dir]
        try:
            main.main()
        except SystemExit as exp:
            assert exp.code == 0
            assert glob.glob(os.path.join(self.tmp_dir, '*.deb')) == []
            assert os.listdir(os.path.join(self.tmp_dir,
                                           'deb_build_test-proj',
                                           'debian')) != []

    def test_build_from_generate(self):
        sys.argv = ['', 'generate', '-p', self.tmp_dir]
        try:
            main.main()
        except SystemExit as exp:
            assert exp.code == 0

        sys.argv = ['', 'build', '-p', self.tmp_dir]
        try:
            main.main()
        except SystemExit as exp:
            assert exp.code == 0
            assert os.path.exists(os.path.join(self.tmp_dir,
                                               'test-proj_0.1.0_all.deb'))
            assert os.path.exists(os.path.join(self.tmp_dir,
                                               'deb_build_test-proj')) is False

    def test_build_from_generate_unclean(self):
        sys.argv = ['', 'generate', '-p', self.tmp_dir]
        try:
            main.main()
        except SystemExit as exp:
            assert exp.code == 0

        sys.argv = ['', 'build', '-p', self.tmp_dir, '--no-clean']
        try:
            main.main()
        except SystemExit as exp:
            assert exp.code == 0
            assert os.path.exists(os.path.join(self.tmp_dir,
                                               'test-proj_0.1.0_all.deb'))
            assert os.listdir(os.path.join(self.tmp_dir,
                                           'deb_build_test-proj',
                                           'debian')) != []