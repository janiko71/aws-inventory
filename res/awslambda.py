import boto3
import botocore
from botocore.exceptions import ClientError
import pprint

def get_lambda_inventory(ownerId, region_name):
    """
        Returns lambda inventory (if the region is avalaible)

        :param region: region name
        :type region: string

        :return: S3 inventory
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/lambda.html
    """
    inventory = []
    try:
        awslambda = boto3.client('lambda')
        print('OwnerID : {}, lambda inventory, Region : {}'.format(ownerId, region_name))
        inventory.append(awslambda.list_functions())
    except:
        print('OwnerID : {}, lambda not supported in region : {}'.format(ownerId, region_name))
    
    return inventory


# Hey, doc: we're in a module!
if (__name__ == '__main__'):
    print('Module => Do not execute')