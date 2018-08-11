import boto3
import botocore
import json
import config
import pprint, operator
import res.utils as utils
import res.glob as glob

# =======================================================================================================================
#
#  Supported services   : KMS
#  Unsupported services : IAM
#
# =======================================================================================================================

#  ------------------------------------------------------------------------
#
#    KMS (Keys Management System)
#
#  ------------------------------------------------------------------------

def get_kms_inventory2(ownerId, region_name):
    """
        Returns keys managed by KMS (global)

        :param ownerId: ownerId (AWS account)
        :type ownerId: string
        :param region: region name
        :type region: string

        :return: KMS inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/kms.html
    """
    config.logger.info('KMS inventory, {}, get_kds_inventory'.format(region_name))

    kms_list = []

    client = boto3.client('kms', region_name)

    for kms in client.list_keys().get('Keys'):
        kms_list.append(client.describe_key(KeyId=kms['KeyId']).get('KeyMetadata'))
    return kms_list


def get_kms_inventory(oId):
    """
        Returns keys managed by KMS (global)

        :param ownerId: ownerId (AWS account)
        :type ownerId: string

        :return: KMS inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/kms.html
    """ 
    kms_inventory = glob.get_inventory(
        ownerId = oId,
        aws_service = "kms", 
        aws_region = "all", 
        function_name = "list_keys", 
        key_get = "Keys",
        detail_function = "describe_key", 
        key_get_detail = "KeyMetadata",
        key_selector = "KeyId=kms['KeyId']"
    )

    ''' client = boto3.client("kms")
    for kms in tmp_inventory:
        print("------",kms['KeyId'])
        kms_inventory.append(client.describe_key(KeyId=kms['KeyId']).get('KeyMetadata'))'''

    return kms_inventory



#
# Hey, doc: we're in a module!
#
#if (__name__ == '__main__'):
#    print('Module => Do not execute')