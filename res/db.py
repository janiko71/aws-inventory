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


#  ------------------------------------------------------------------------
#
#    DynamoDB 
#
#  ------------------------------------------------------------------------

def get_dynamodb_inventory(ownerId, region_name):
    """
        Returns dynamoDB inventory

        :param ownerId: ownerId (AWS account)
        :type ownerId: string
        :param region_name: region name
        :type region_name: string

        :return: dynamoDB inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/dynamodb.html
                 if the region is not supported, an exception is raised (EndpointConnectionError 
                 or AccessDeniedException)
    """
    config.logger.info('dynamoDB inventory, region {}, get_rds_inventory'.format(region_name))

    client = boto3.client('dynamodb', region_name)
    ddb_list = client.list_tables().get('TableNames')
    ddb_inventory = []
    for ddb in ddb_list:
        ddb_inventory.append(client.describe_table(TableName=ddb).get('Table'))

    return ddb_inventory

#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')