import os
from subprocess import Popen, PIPE, STDOUT
import logging
import shutil

import semantic_version as sv
import sys
import virtualenv

import debpackager.packages.conf.configurations as cfg

logger = logging.getLogger(__name__)


def get_new_version(extra_args):
    custom_version = extra_args.get('custom_version')
    if custom_version:
        if sv.validate(custom_version):
            return custom_version
        logger.error(
            'The given version format is invalid. value was: {}, please set '
            'version in format (major.minor.patch) like - 2.1.0'.format(
                custom_version))
        raise Exception(
            'version format is invalid. supplied version: {}'
                .format(custom_version))

    version = extra_args.get('pom').project.get('version')
    if not version:
        raise Exception(
            'Could not get a valid version, please check project.json')

    if not sv.validate(version):
        raise Exception(
            'version format is invalid. value is: {}'.format(version))

    version = sv.Version(version)

    return str(version)


def run_command(command):
    logger.debug('running command: {}'.format(command))
    if type(command) == list:
        command = " ".join(command)
    proc = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True)
    while proc.poll() is None:
        line = proc.stdout.readline().strip()
        if line:
            logger.info(line)

    stdo, erro = proc.communicate()
    if stdo:
        logger.info(stdo)
    if erro:
        logger.info(erro)
    if proc.returncode != 0:
        raise Exception('failed to run command, {}: {}'.format(stdo, command))

    return proc.returncode


def create_virtual_env(project_path, install_path):
    # remove existing virtual env if exists
    ve_path = os.path.join(project_path, cfg.VIRTUAL_ENV_PATH)
    if os.path.exists(ve_path):
        shutil.rmtree(ve_path)
    try:
        logger.info('creating virtual env')
        virtualenv.create_environment(ve_path)
    except Exception:
        logger.exception('failed to create virtualenv: ')
        raise Exception('failed to create virtualenv!')
    try:
        logger.info('installing requirements for virtualenv')
        # update pip to latest version
        run_command(['{}/ve/bin/pip'.format(project_path),
                     'install',
                     '-U',
                     'pip'])

        if not os.path.exists('{}/requirements.txt'.format(project_path)):
            logger.warning('requirements.txt not found')
            return ve_path

        run_command(['{}/ve/bin/pip'.format(project_path),
                     'install',
                     '-r',
                     '{}/requirements.txt'.format(project_path)])
        virtualenv.make_environment_relocatable(ve_path)
        fixup_scripts(install_path, ve_path)
    except Exception:
        logger.exception('failed to install requirements! error message:')
        raise Exception('fail to install requirements.')
    return ve_path


def fixup_scripts(deploy_ve_home_dir, ve_path):
    """ fixes the shebang line in virtualenv bin dir scripts
    to be where the package virtualenv was deployed

    :param deploy_ve_home_dir:
    :param ve_path: (str) path where virtualenv is located after installation
    """
    ok_abs_scripts = ['python', 'python%s' % sys.version[:3],
                      'activate', 'activate.bat', 'activate_this.py',
                      'activate.fish', 'activate.csh']
    if not deploy_ve_home_dir:
        return

    bin_dir = os.path.join(ve_path, 'bin')
    # This is what we expect at the top of scripts:
    shebang = '#!{} python{}'.format('/usr/bin/env', sys.version[:3])
    # This is what we'll put:
    new_shebang = '#!{}/{}/bin/python{}'.format(deploy_ve_home_dir,
                                                cfg.VIRTUAL_ENV_PATH,
                                                sys.version[:3])

    for filename in os.listdir(bin_dir):
        filename = os.path.join(bin_dir, filename)
        if not os.path.isfile(filename):
            # ignore subdirs, e.g. .svn ones.
            continue
        lines = None
        with open(filename, 'rb') as f:
            try:
                lines = f.read().decode('utf-8').splitlines()
            except UnicodeDecodeError:
                # This is probably a binary program instead
                # of a script, so just ignore it.
                continue
        if not lines:
            logger.warn('Script %s is an empty file' % filename)
            continue

        old_shebang = lines[0].strip()
        old_shebang = old_shebang[0:2] + os.path.normcase(old_shebang[2:])

        if not old_shebang.startswith(shebang):
            if os.path.basename(filename) in ok_abs_scripts:
                logger.debug('Cannot make script %s relative' % filename)
            elif lines[0].strip() == new_shebang:
                logger.info('Script %s has already been made relative' % filename)
            else:
                logger.warn('Script %s cannot be made relative '
                            '(it\'s not a normal script that starts with %s)'
                            % (filename, shebang))
            continue
        logger.info('Making script %s relative' % filename)
        with open(filename, 'wb') as f:
            f.write('\n'.join([new_shebang] + lines[1:]).encode('utf-8'))


def install_deb_dependencies(extra_args):
    debs_to_install = extra_args.get('pom').project.get('deb_dependencies', [])
    if not debs_to_install:
        logger.warning('Not installing deb dependencies')
        return
    command = ['sudo', 'apt-get', 'install', '-y', '--force-yes']
    command.extend(debs_to_install)
    run_command(command)
