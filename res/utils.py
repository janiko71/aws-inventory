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

def display(ownerId, function, region_name, function_name):

    '''
        Formatting display output, with progression (in %)
    '''
    progression = (config.nb_units_done / config.nb_units_todo * 100)
    print(config.display.format(ownerId, progression, function, region_name, function_name, " "*20), end="\r", flush=True)
    return

def progress(region_name):

    '''
        Shows job progression, depending on services passed in arguments
    '''

    if (region_name == "global"):
        config.nb_units_done = config.nb_units_done + config.nb_regions
    else:        
        config.nb_units_done = config.nb_units_done + 1
    config.logger.debug("config.nb_units_done {} config.nb_units_todo {}".format(config.nb_units_done, config.nb_units_todo))        
    return


def check_arguments(arguments):

    """
        Check if the arguments (in command line) are known. If not, we raise an exception.

        We also look for the debug level. If we found it, we adjust the log level but we don't include it in the service list.

        :param arguments: list of arguments
        :type arguments: list

        :return: owner ID
        :rtype: string
    """   

    new_arguments = []
    for arg in arguments:
        if (arg not in config.SUPPORTED_COMMANDS) and (arg not in config.SUPPORTED_PARAMETERS):
            raise Exception('Unknown argument [' + arg + ']')
        if (arg == "debug"):
            config.logger.setLevel(logging.DEBUG)
        elif (arg == "info"):
            config.logger.setLevel(logging.INFO)
        elif (arg == "warning"):
            config.logger.setLevel(logging.WARNING)
        elif (arg == "error"):
            config.logger.setLevel(logging.ERROR)
        else:
            new_arguments.append(arg)
    return new_arguments


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

#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')