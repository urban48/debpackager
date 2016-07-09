
import os
import json
import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)


class Pom(object):
    """ Class responsible from managing project setting file

    """
    project_file_name = 'project.json'

    def __init__(self, project_path):
        self.project_path = os.path.join(project_path, self.project_file_name)
        self.project = self._get_project()

    def _get_project(self):
        """ loads project information from file

        :return: (dict) settings in json format
        """
        try:
            with open(self.project_path, 'r') as f:
                project = json.loads(f.read(), object_pairs_hook=OrderedDict)
                return project
        except ValueError as e:
            logger.error('{} format is incorrect: {}'
                         .format(self.project_file_name, e))
            raise ValueError
        except IOError:
            logger.info('Could not open {}'.format(self.project_path))
            return {}

    def set_version(self, version):
        """ update project version

        :param version: (str) version number
        """
        try:
            with open(self.project_path, 'w') as wf:
                self.project['version'] = version
                wf.write(json.dumps(self.project, indent=2))
        except IOError:
            raise Exception('Could not open {} to set version'
                .format(self.project_path + '/' + self.project_file_name))
