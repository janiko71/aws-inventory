import boto3
import botocore
from botocore.exceptions import ClientError
import pprint
import logging
import json
import datetime
import time
import dateutil
from dateutil.tz import tzutc
import config

#
#  Useful functions
#

def display(ownerId, function, region_name):
    print(config.display.format(ownerId, function, region_name))
    return


def check_arguments(arguments):
    """
        Check if the arguments (in command line) are known.

        :param arguments: list of arguments
        :type arguments: list

        :return: owner ID
        :rtype: string
    """   
    for arg in arguments:
        if (arg not in config.SUPPORTED_COMMANDS):
            raise Exception('Unknown argument [' + arg + ']')
    return 


def get_ownerID():
    """
        Get owner ID of the AWS account we are working on

        :return: owner ID
        :rtype: string
    """   
    sts = boto3.client('sts')
    identity = sts.get_caller_identity()
    ownerId = identity['Account']
    return ownerId


def datetime_converter(dt):
    """
        Converts a python datetime object (returned by AWS SDK) into a readable and SERIALIZABLE string

        :param dt: datetime
        :type dt: datetime

        :return: datetime in a good format
        :rtype: str
    """
    if isinstance(dt, datetime.datetime):
        return dt.__str__()  


def json_datetime_converter(json_text):
    """
        Parses a json object and converts all datetime objects (returned by AWS SDK) into str objects

        :param json_text: json with datetime objects
        :type json_text: json

        :return: json with date in string format
        :rtype: json
    """
    return json.dumps(json_text, default = datetime_converter)      

