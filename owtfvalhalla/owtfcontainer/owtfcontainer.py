"""
This is iteration 1 of the OwtfContainer.
Dont use! Look at iteration 2 instead.
"""

import os
import pprint
import json
import logging

from dclient import *

LOG = logging.getLogger(__name__)


class OwtfContainer(object):

    def __init__(self, image_path):
        self.container_id = None
        self.image_id = None
        self.container_instance_id = None  # This should be implemented for mulit cotainers of the same
        self.config_file_json = None
        self.log = ''
        self.is_image_build = False
        self.is_container_build = False
        self.is_valid = False
        self.is_running = False

        self.container_info = None  # This is data we get from: cli.containers(all=True)
        self.container_ip_address = None

        self.image_path = os.path.abspath(image_path)
        self.dockerfile_path = os.path.join(os.path.abspath(image_path), 'Dockerfile')
        self.config_file_path = os.path.join(os.path.abspath(image_path), 'config.json')
        self.read_config_file()
        self.container_name = self.config_file_json['title'].lower()  # Tag files needs to be lowercase
        self.container_version = self.config_file_json['version']
        self.container_tag = self.container_name+':'+self.container_version
        self.validate_config_and_dockerfile()

    def validate_config_and_dockerfile(self):
        """Validates the obj. Check if all files and folder are correct and
        check if images and containers are in place.
        """
        if not os.path.isdir(self.image_path):
            LOG.debug('container_path is not a dir')
            self.is_valid = False
            return

        elif not os.path.isfile(os.path.join(self.image_path, 'Dockerfile')):
            LOG.debug('dockerfile_path is not a file or does not exist')
            self.is_valid = False
            return

        elif not os.path.isfile(self.config_file_path):
            LOG.debug('config_file_path is not a file or does not exist')
            self.is_valid = False
            return

        elif not self.read_config_file():  # Read the config file
            LOG.debug('failed to parse config file to json')
            self.is_valid = False
            return

        else:
            LOG.debug('validate_config_and_dockerfile success!')
            self.is_valid = True

        # Check if container image is already build.
        if self.is_valid:
            for image in cli.images():
                if self.container_tag == image['RepoTags'][0]:
                    self.is_image_build = True

        # Check if container is already build.
        if self.is_valid:
            for c in cli.containers(all=True):
                if c['Names'][0] == '/'+self.container_name+'_'+self.container_version:
                    self.is_container_build = True

        # Check if container is running
        if self.is_valid and self.is_image_build and self.is_container_build:
            for cont in cli.containers():
                if cont['Image'] == self.container_tag:
                    self.is_running = True
                    self.container_id = cont['Id']
                    # GET THE IP ADDRESS

            # if self.container_tag in [c['Image'] for c in cli.containers()]:
            #     self.is_running = True

    def read_config_file(self):
        """Read config.json and assign it to self.config_file_json"""
        try:
            with open(self.config_file_path) as data_file:
                self.config_file_json = json.load(data_file)
                return True
        except ValueError as e:
            print('Cant parse config file to json')
            print(e)  # Log this
            return False

    def build_image(self):
        """Build image from Dockerfile, tag is self.container_tag"""
        if self.is_valid and not self.is_image_build:
            LOG.debug('Container is valid and is not build.')
            for i in cli.build(path=self.image_path, rm=True, tag=self.container_tag):
                self.log += str(i)
            self.is_image_build = True

    def build_container(self):
        """Build the container from image, tag is self.container_tag"""
        if self.is_valid and self.is_image_build and not self.is_container_build:
            container = cli.create_container(
                name=self.container_name+'_'+self.container_version,
                image=self.container_tag,
                command='app.py'
            )
            self.container_id = container.get('Id')
            self.is_container_build = True

    def start(self):
        """Start container and get the IP"""
        if self.is_valid and self.is_image_build and self.is_container_build:
            cli.start(container=self.container_id)
            c_info = cli.inspect_container(container=self.container_id)
            self.is_running = True
            self.container_ip_address = c_info['NetworkSettings']['Networks']['bridge']['IPAddress']

    def stop(self):
        if self.is_running:
            cli.stop(container=self.container_id)
            self.is_running = False

    def restart(self):
        self.stop()
        self.start()

    def remove_image(self):
        if self.is_image_build:
            cli.remove_image(
                image=self.container_tag,
                force=True
            )
            self.is_image_build = False

    def remove_container(self):
        if self.is_container_build:
            cli.remove_container(
                container=self.container_name+'_'+self.container_version,
                force=True
            )
            self.is_container_build = False
        else:
            return None

    def inspect(self):
        if self.is_running:
            return cli.inspect_container(container=self.container_id)
        return None

    def __repr__(self):
        """Gives a nice json-like output for debug."""
        return pprint.pformat(self.__dict__, indent=4)

    def __str__(self):
        return 'OwtfContainer({}, {})'.format(self.container_name, self.container_version)
