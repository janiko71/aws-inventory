import boto3
import botocore
import json
import config
import res.utils as utils


#  ------------------------------------------------------------------------
#
#    RDS 
#
#  ------------------------------------------------------------------------

def get_rds_inventory(ownerId, region_name):
    """
        Returns RDS inventory

        :param ownerId: ownerId (AWS account)
        :type ownerId: string
        :param region_name: region name
        :type region_name: string

        :return: RDS inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/rds.html
                 if the region is not supported, an exception is raised (EndpointConnectionError 
                 or AccessDeniedException)
    """
    config.logger.info('RDS inventory, region {}, get_rds_inventory'.format(region_name))

    client = boto3.client('rds', region_name)
    rds_list = client.describe_db_instances().get('DBInstances')

    return rds_list


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')