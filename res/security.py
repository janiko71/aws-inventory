import boto3
import botocore
import json
import config
import res.utils as utils
import res.glob  as glob

# =======================================================================================================================
#
#  Supported services   : Directory Service 
#  Unsupported services : Cognito, Secrets Manager, GuardDuty, Inspector, Amazon Macie, AWS Single Sign-On, Certificate Manager, CloudHSM, 
#                           WAF & Shield, Artifact
#
#  Note: IAM has its own module
#
# =======================================================================================================================

#  ------------------------------------------------------------------------
#
#    Cloud Directory (simple)
#
#  ------------------------------------------------------------------------

def get_clouddirectory_inventory(oId):
    """
        Returns keys managed by KMS (global)

        :param ownerId: ownerId (AWS account)
        :type ownerId: string

        :return: KMS inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/kms.html
    """ 
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "clouddirectory", 
        aws_region = "all", 
        function_name = "list_directories", 
        key_get = "Directories"
    )


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')