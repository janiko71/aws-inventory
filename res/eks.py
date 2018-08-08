import boto3
import botocore
from botocore.exceptions import ClientError
import pprint

def get_eks_inventory(ownerId, region_name):
    """
        Returns eks inventory (if the region is avalaible)

        :param region: region name
        :type region: string

        :return: S3 inventory
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/eks.html
    """
    inventory = []
    try:
        eks = boto3.client('eks')
        print('OwnerID : {}, EKS inventory, Region : {}'.format(ownerId, region_name))
        inventory.append(eks.list_clusters())
    except:
        print('OwnerID : {}, EKS not supported in region : {}'.format(ownerId, region_name))
    
    return inventory


# Hey, doc: we're in a module!
if (__name__ == '__main__'):
    print('Module => Do not execute')