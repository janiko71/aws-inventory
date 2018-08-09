import boto3
import botocore
from botocore.exceptions import ClientError
import pprint

def get_lambda_inventory(ownerId):
    """
        Returns lambda inventory.

        :param region: region name
        :type region: string

        :return: S3 inventory
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/lambda.html
    """
    awslambda = boto3.client('lambda')
    print('OwnerID : {}, lambda inventory, Region : {}'.format(ownerId, 'all regions'))
    lambda_list = awslambda.list_functions().get('Functions')
   
    return lambda_list


# Hey, doc: we're in a module!
if (__name__ == '__main__'):
    print('Module => Do not execute')