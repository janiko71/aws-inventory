import boto3
import botocore
import json
import config
import res.utils as utils

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

def get_kms_inventory(ownerId, region_name):
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

    client = boto3.client('kms', region_name)
    kms_list = []
    for kms in client.list_keys().get('Keys'):
        kms_list.append(client.describe_key(KeyId=kms['KeyId']).get('KeyMetadata'))
    return kms_list


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')