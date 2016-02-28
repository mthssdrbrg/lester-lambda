# -*- coding: utf-8 -*-
""" AWS Lambda function for checking when a SSL certificate is expiring. """

from __future__ import print_function
import socket
import ssl
import datetime
import ConfigParser
import json
import boto3


def read_config():
    """ Read configuration file. """
    config = ConfigParser.SafeConfigParser()
    config.read('config.ini')
    return config


def expires_at(hostname):
    """ Fetch expire date for SSL certificate. """
    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'
    context = ssl.create_default_context()
    conn = context.wrap_socket(
        socket.socket(socket.AF_INET),
        server_hostname=hostname,
        )
    conn.settimeout(3.0)
    conn.connect((hostname, 443))
    ssl_info = conn.getpeercert()
    return datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)


def notify(topic, message):
    """ Publish message to SNS topic. """
    sns = boto3.client('sns')
    sns.publish(TopicArn=topic, Message=json.dumps(message))
    return


def handle(event, _):
    """ Check if certificate for LESTER_DOMAIN is expiring soon. """
    config = read_config()
    domain = config.get('lester', 'domain')
    buffer_days = config.getint('expire', 'buffer_days')
    topic = config.get('expire', 'topic')
    expires = expires_at(domain)
    print('Certificate for %s expires at %s' % (domain, expires))
    remaining = expires - datetime.datetime.utcnow()
    if remaining < datetime.timedelta(days=0):
        notify(topic, {domain: remaining})
    elif remaining < datetime.timedelta(days=buffer_days):
        notify(topic, {domain: remaining})
    else:
        print('Certificate expires in %s' % remaining)
    return event
