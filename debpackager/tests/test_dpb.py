import os
import tempfile
import shutil

import pytest

from debpackager.utils.debain_package_manager import Dpm


@pytest.mark.unitest
class TestDpb(object):
    """
     unit tests for debian package builder module
    """

    def setup_method(self, method):
        """ setup any state tied to the execution of the given method in a
        class.  setup_method is invoked for every test method of a class.
        """
        self.tmpdir = tempfile.mkdtemp()
        self.dpb = Dpm(self.tmpdir, 'test-proj',
                       '1.0.0', self.tmpdir + '/install')

    def teardown_method(self, method):
        """ teardown any state that was previously setup with a setup_method
        call.
        """
        shutil.rmtree(self.tmpdir)

    def test_dh_make(self):
        """ Test if method created debian folder with default files"""
        assert self.dpb._dh_make() == 0
        assert os.path.exists(self.dpb.debian_package_path + '/debian') is True

    def test_create_install_file(self):
        """ test that install file is created"""
        self.dpb._dh_make()
        self.dpb._create_install_file()

        install_file_path = self.dpb.debian_package_path + \
                            '/debian/test-proj.install'

        assert os.path.exists(install_file_path) is True
        install_content = '../{}/* {}\n'.format(os.path.basename(self.tmpdir),
                                                self.tmpdir + '/install')

        with open(install_file_path, 'r') as inst_file:
            assert install_content in inst_file.read()

    def test_add_deb_dependencies(self):
        """ make sure deb dependencies are parsed and added properly"""
        self.dpb._dh_make()
        self.dpb.dependencies = ['deb1>=0.1.2', 'deb2']
        self.dpb._add_deb_dependencies()

        control_file_path = self.dpb.debian_package_path + '/debian/control'

        dependencies_string = 'Depends: ${misc:Depends}, deb1(>=0.1.2), deb2'

        with open(control_file_path, 'r') as inst_file:
            assert dependencies_string in inst_file.read()

    def test_set_exclude(self):
        """ verifies that debian excludes are added"""
        self.dpb._dh_make()
        self.dpb.excludes = ['.pyc', 'doc', 'specs.cfg']
        self.dpb._set_exclude()

        rules_file_path = self.dpb.debian_package_path + '/debian/rules'

        dependencies_string = '\tdh_install -X .pyc -X doc -X specs.cfg'
        with open(rules_file_path, 'r') as inst_file:
            assert dependencies_string in inst_file.read()

    def test_add_maintainer_scripts(self):
        """ verify maintainern scripts if exists added to debian"""
        os.mkdir(self.tmpdir + '/debian')
        with open(self.tmpdir + '/debian/postinst', 'w') as post_file:
            post_file.write('echo "im a custom postinst script"')

        self.dpb._dh_make()
        self.dpb._add_maintainer_scripts()

        postinst_file_path = self.dpb.debian_package_path + \
                             '/debian/test-proj.postinst'

        postinst_content = 'echo "im a custom postinst script"'
        with open(postinst_file_path, 'r') as inst_file:
            assert postinst_content in inst_file.read()

    def test_add_maintainer_scripts_no_debian_dir(self):
        """ check that maintainer scripts not created, and no errors thrown
        if no debian dir exists"""
        self.dpb._dh_make()
        self.dpb._add_maintainer_scripts()

        postinst_file_path = self.dpb.debian_package_path + \
                             '/debian/test-proj.postinst'

        assert os.path.exists(postinst_file_path) is False

    def test_add_startup_script_upstart(self):
        """ verify that upstart script is added correctly"""
        os.mkdir(self.tmpdir + '/debian')
        with open(self.tmpdir + '/debian/ad-server.upstart', 'w') as up_file:
            up_file.write('echo "im a upstart script"')

        self.dpb._dh_make()
        self.dpb._add_startup_script()

        upstart_file_path = self.dpb.debian_package_path + \
                            '/debian/ad-server.upstart'

        upstart_content = 'echo "im a upstart script"'
        with open(upstart_file_path, 'r') as inst_file:
            assert upstart_content in inst_file.read()

    def test_add_startup_script_initd(self):
        """ verify that init.d script is added correctly"""
        os.mkdir(self.tmpdir + '/debian')
        with open(self.tmpdir + '/debian/ad-server.init', 'w') as init_file:
            init_file.write('echo "im a init script"')

        self.dpb._dh_make()
        self.dpb._add_startup_script()

        init_file_path = self.dpb.debian_package_path + \
                         '/debian/ad-server.init'

        init_content = 'echo "im a init script"'
        with open(init_file_path, 'r') as inst_file:
            assert init_content in inst_file.read()

    def test_add_startup_script_no_deb_dir(self):
        """ check that no errors thrown if no deb dir exists"""
        self.dpb._dh_make()
        self.dpb._add_startup_script()

        upstart_file_path = self.dpb.debian_package_path + \
                            '/debian/ad-server.upstart'
        assert os.path.exists(upstart_file_path) is False

        init_file_path = self.dpb.debian_package_path + \
                         '/debian/ad-server.init'
        assert os.path.exists(init_file_path) is False
