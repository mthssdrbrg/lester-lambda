# -*- coding: utf-8 -*-
""" AWS Lambda function for renewing a Let's Encrypt SSL certificate. """
from distutils import dir_util
import subprocess
import os
import ConfigParser


def read_config():
    """ Read configuration file. """
    config = ConfigParser.SafeConfigParser()
    config.read('config.ini')
    return config


def handle(event, _):
    """ Renew certificate using configuration from LESTER_* variables. """
    dir_util.copy_tree('lester', '/tmp')
    config = read_config()
    command = [
        '/tmp/lester',
        'renew',
        '--domain', config.get('lester', 'domain'),
        '--site-bucket', config.get('lester', 'site_bucket'),
        '--storage-bucket', config.get('lester', 'storage_bucket'),
        '--distribution-id', config.get('lester', 'distribution_id'),
        ]
    if config.has_option('lester', 'kms_id'):
        command.extend(['--kms-id', config.get('lester', 'kms_id')])
    env = dict(os.environ.copy(), LC_ALL='en_US.UTF-8')
    subprocess.check_call(command, stderr=subprocess.STDOUT, env=env)
    return event
