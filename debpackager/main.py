import os
import sys
import logging
import argparse
from logging.config import dictConfig

from utils.general import run_command
from debpackager.utils.pom import Pom
from debpackager.conf.log_conf import LOG_CONF

__version__ = '0.1.0'

logger = logging.getLogger(__name__)


def main():
    dictConfig(LOG_CONF)
    args = parse_arguments()

    pom = Pom(project_path=args.project_path)
    if not pom.project:
        logger.error('Could not find project.json at {}'
                     .format(args.project_path))
        sys.exit(1)

    project_args = vars(add_missing_params(parse_arguments(), pom))
    if not project_args:
        return
    exit_code = 0
    try:
        # get the requested type module and init it
        package = getattr(getattr(getattr(getattr(__import__(
            'debpackager.packages.{0}.{0}'
            .format(project_args['project_type'])),
            'packages'),
            project_args['project_type']),
            project_args['project_type']),
            project_args['project_type'].capitalize())(project_args)

        if project_args['action'] == 'build':
            logger.info('Using package version: {}'.format(__version__))

        # execute the action
        getattr(package, project_args['action'])()
    except Exception as exp:
        logger.error(u"ERROR: {}\n".format(exp))
        exit_code = 1
    finally:
        if package and args.clean:
            for item in package.extra_files:
                path_to_delete = os.path.join(args.project_path, item)
                if os.path.exists(path_to_delete):
                    run_command(['rm', '-rf', path_to_delete])
        sys.exit(exit_code)


def parse_arguments():

    types = ['python', 'general']

    parser = argparse.ArgumentParser(description=
                                     'cli tool for creating debians',
                                     add_help=False)
    parser.add_argument('-v', '--version', help='show version',
                        action='version', version=__version__)
    parser.add_argument('-h', '--help', action=_HelpAction,
                        help='show help')

    subparsers = parser.add_subparsers()

    build = subparsers.add_parser('build')
    build.set_defaults(action='build')
    build.add_argument('--install-dependencies',
                       dest='install_dependencies',
                       action='store_true',
                       help='install deb dependencies before build\n'
                            '(used for python virtualenv creation)',
                       default=False)
    build.add_argument('--no-clean',
                       dest='clean',
                       action='store_false',
                       help='leave behind everything used to '
                            'create the debian package',
                       default=True)
    build.add_argument('-t', '--type',
                       metavar='',
                       dest='project_type',
                       action='store',
                       choices=types,
                       help='set project type, default: auto detect')
    build.add_argument('-p', '--path', metavar='', dest='project_path',
                       action='store', default=os.getcwd(),
                       help='set path to project, '
                            'default: current location')
    build.add_argument('-v', '--version', metavar='', dest='custom_version',
                       help='set version manually', action='store')

    return parser.parse_args()


class _HelpAction(argparse._HelpAction):

    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()

        # retrieve subparsers from parser
        subparsers_actions = [
            action for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)]

        for subparsers_action in subparsers_actions:
            # get all subparsers and print help
            print
            for choice, subparser in subparsers_action.choices.items():
                print(choice)
                print('*'*len(choice))
                print(subparser.format_help())

        parser.exit()


def add_missing_params(args, pom):
    """ fill in undefined parameters that are necessary.

    :param args: arguments from argparse
    :param pom: Project object created from project.json
    :return: modified args
    """

    if 'project_path' not in args:
        args.project_path = os.getcwd()

    if not getattr(pom, 'project', {}):

        if 'project_name' not in args:
            args.project_name = os.path.basename(os.getcwd())

        if 'project_type' not in args or not vars(args).get('project_type'):
            args.project_type = get_project_type(args.project_path)

    if 'project_name' not in args:
        args.project_name = pom.project.get('name',
                                            os.path.basename(os.getcwd()))

    if 'project_type' not in args or not vars(args).get('project_type'):
        args.project_type = pom.project.get('type')
        if not args.project_type:
            logger.error('project.json is missing type attribute. '
                         'using general type as default')
            pom.project['type'] = 'general'
            args.project_type = 'general'

    args.pom = pom
    return args


def get_project_type(project_path):
    """ Tries to determine project type, if fails, falls back to general type

    :param project_path: path to project
    :return: (str) type
    """
    if not os.path.exists(project_path):
        raise Exception('Could not find project path: {}'.format(project_path))

    if os.path.exists(os.path.join(project_path, 'requirements.txt')) and not \
       os.path.exists(os.path.join(project_path, 'setup.py')):
        return 'python'

    else:
        logger.warning('Failed to detect project type. '
                       'please use --type, using general type')
        return 'general'

if __name__ == '__main__':
    main()
