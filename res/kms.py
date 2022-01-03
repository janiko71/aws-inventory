import boto3
import botocore
import json
import config
import pprint, operator
import res.utils as utils
import res.glob as glob

"""
Supported services   : KMS
"""

def get_kms_inventory(oId, profile,boto3_config,selected_regions):

    """
        Returns keys managed by KMS (global)

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: KMS inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/kms.html
    """ 
    
    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = "global",
        aws_service = "kms", 
        aws_region = "all", 
        function_name = "list_keys", 
        key_get = "Keys",
        detail_function = "describe_key", 
        join_key = "KeyId", 
        detail_join_key = "KeyId", 
        detail_get_key = "KeyMetadata",
        pagination = True
    )

''' Hey, doc: we're in a module! '''

if (__name__ == '__main__'):
    print('Module => Do not execute')
