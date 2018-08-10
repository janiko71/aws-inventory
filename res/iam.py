import boto3
import botocore
import json
import config
import res.utils as utils


#  ------------------------------------------------------------------------
#
#    KMS (Keys Management System)
#
#  ------------------------------------------------------------------------

def get_kms_inventory(ownerId):
    """
        Returns keys managed by KMS (global)

        :param ownerId: ownerId (AWS account)
        :type ownerId: string

        :return: KMS inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/kms.html
    """
    config.logger.info('KMS inventory, all regions, get_kds_inventory')

    client = boto3.client('kms')
    kms_list = client.list_keys().get('Keys')
    return kms_list


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')