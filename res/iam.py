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

def get_kms_inventory(oId):

    """
        Returns keys managed by KMS (global)

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: KMS inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/kms.html
    """ 
    
    return glob.get_inventory(
        ownerId = oId,
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


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')