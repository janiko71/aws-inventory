import boto3
import botocore
import json
import config
import res.utils as utils
import res.glob  as glob

# =======================================================================================================================
#
#  Supported services   : Directory Service, Secrets Manager, Certificate Manager, CloudHSM 
#  Unsupported services : Cognito, GuardDuty, Inspector, Amazon Macie, AWS Single Sign-On, Certificate Manager PCA, 
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

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: clouddirectory inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/clouddirectory.html
    """ 

    return glob.get_inventory(
        ownerId = oId,
        aws_service = "clouddirectory", 
        aws_region = "all", 
        function_name = "list_directories", 
        key_get = "Directories",
        pagination = True
    )


#  ------------------------------------------------------------------------
#
#    ACM (Certificate Manager)
#
#  ------------------------------------------------------------------------

def get_acm_inventory(oId):

    """
        Returns certificates managed with ACM

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: certificates inventory
        :rtype: json

        ..note:: https://boto3.readthedocs.io/en/latest/reference/services/acm.htm
    """ 

    return glob.get_inventory(
        ownerId = oId,
        aws_service = "acm", 
        aws_region = "all", 
        function_name = "list_certificates", 
        key_get = "CertificateSummaryList",
        detail_function = "describe_certificate", 
        join_key = "CertificateArn", 
        detail_join_key = "CertificateArn", 
        detail_get_key = "Certificate",
        pagination = True
    )


#  ------------------------------------------------------------------------
#
#    ACMPCA (Certificate Manager Private Certificate Authority). Not implemented yet.
#
#  ------------------------------------------------------------------------

def get_acmpca_inventory(oId):

    """
        Returns certificates managed with ACM

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: certificates inventory
        :rtype: json

        ..note:: https://boto3.readthedocs.io/en/latest/reference/services/acm-pca.html
    """ 
    
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "acm-pca", 
        aws_region = "all", 
        function_name = "list_certificate_authorities", 
        key_get = "CertificateAuthorities"
    )


#  ------------------------------------------------------------------------
#
#    Secrets Manager
#
#  ------------------------------------------------------------------------

def get_secrets_inventory(oId):

    """
        Returns all secrets managed by AWS (without values of the secrets ;-)

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: secrets inventory 
        :rtype: json

        ..note:: https://boto3.readthedocs.io/en/latest/reference/services/acm-pca.html
    """ 
    
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "secretsmanager", 
        aws_region = "all", 
        function_name = "list_secrets", 
        key_get = "SecretList"
    )


#  ------------------------------------------------------------------------
#
#    CloudHSM 
#
#  ------------------------------------------------------------------------

def get_hsm_inventory(oId):

    """
        Returns cloud HSM inventory

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: HSM inventory
        :rtype: json

        ..note:: https://boto3.readthedocs.io/en/latest/reference/services/CloudHSM.html
    """ 
    inventory = {}

    inventory['clusters'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "cloudhsmv2", 
        aws_region = "all", 
        function_name = "describe_clusters", 
        key_get = "Clusters",
        pagination = True
    )

    inventory['hsm'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "cloudhsm", 
        aws_region = "all", 
        function_name = "list_hsms", 
        key_get = "HsmList",
        detail_function = "describe_hsm", 
        join_key = "", 
        detail_join_key = "HsmArn", 
        detail_get_key = ""
    )

    inventory['luna'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "cloudhsm", 
        aws_region = "all", 
        function_name = "list_luna_clients", 
        key_get = "ClientList",
        detail_function = "describe_luna_client", 
        join_key = "", 
        detail_join_key = "ClientArn", 
        detail_get_key = ""
    )

    return inventory


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')