import boto3
import botocore
import json
import config
import res.utils as utils
import res.glob  as glob


"""
    Supported services   : Directory Service, Secrets Manager, Certificate Manager, CloudHSM (broken for now), WAF & Shield, GuardDuty
    Unsupported services : Cognito, Inspector, Amazon Macie, AWS Single Sign-On, Certificate Manager PCA, 
                           Artifact, Security Hub, Detective, AWS Audit Manager, Directory Service, AWS Signer,
                           AWS Network Firewall
    Note: IAM has its own module
"""

def get_clouddirectory_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns clouddirectory inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: clouddirectory inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/clouddirectory.html
    """ 

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "clouddirectory", 
        aws_region = "all", 
        function_name = "list_directories", 
        key_get = "Directories",
        pagination = True
    )

def get_acm_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns certificates managed with ACM

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: certificates inventory
        :rtype: json

        ..note:: https://boto3.readthedocs.io/en/latest/reference/services/acm.htm
    """ 

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
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


def get_acmpca_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns certificates managed with ACM

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: certificates inventory
        :rtype: json

        ..note:: https://boto3.readthedocs.io/en/latest/reference/services/acm-pca.html
    """ 
    
    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "acm-pca", 
        aws_region = "all", 
        function_name = "list_certificate_authorities", 
        key_get = "CertificateAuthorities"
    )

def get_secrets_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns all secrets managed by AWS (without values of the secrets ;-)

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: secrets inventory 
        :rtype: json

        ..note:: https://boto3.readthedocs.io/en/latest/reference/services/acm-pca.html
    """ 
    
    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "secretsmanager", 
        aws_region = "all", 
        function_name = "list_secrets", 
        key_get = "SecretList"
    )

def get_hsm_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns cloud HSM inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: HSM inventory
        :rtype: json

        ..note:: https://boto3.readthedocs.io/en/latest/reference/services/CloudHSM.html
    """ 
    inventory = {}

    inventory['clusters'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "cloudhsmv2", 
        aws_region = "all", 
        function_name = "describe_clusters", 
        key_get = "Clusters",
        pagination = True
    )

    # The API hangs here. Issue #06
    # Removed for it seems not working
    """
    inventory['hsm'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
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
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "cloudhsm", 
        aws_region = "all", 
        function_name = "list_luna_clients", 
        key_get = "ClientList",
        detail_function = "describe_luna_client", 
        join_key = "", 
        detail_join_key = "ClientArn", 
        detail_get_key = ""
    )
    """
    return inventory


def get_waf_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns WAF, WAFv2 & WAF Regional inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: HSM inventory
        :rtype: json

        ..note:: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/waf.html
        ..note:: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/wafv2.html
        ..note:: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/waf-regional.html
        
    """ 
    inventory = {}

    inventory['waf'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "waf", 
        aws_region = "global", 
        function_name = "list_rules", 
        key_get = "Rules",
        pagination = True
    )


    inventory['wafv2'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "wafv2", 
        aws_region = "global", 
        function_name = "list_rule_groups", 
        key_get = "RuleGroups",
        pagination = True
    )

    inventory['waf-regional'] = {}
    
    inventory['waf-regional']['web_acls'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "waf-regional", 
        aws_region = "all", 
        function_name = "list_web_acls", 
        key_get = "WebACLs",
        pagination = False
    )
    
    inventory['waf-regional']['rules'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "waf-regional", 
        aws_region = "all", 
        function_name = "list_rules", 
        key_get = "Rules",
        pagination = False
    )

    return inventory

def get_guardduty_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns GuardDuty inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: GuardDuty inventory
        :rtype: json

        ..note:: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/guardduty.html
        
    """ 
    inventory = {}

    inventory['detectors'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "guardduty", 
        aws_region = "all", 
        function_name = "list_detectors", 
        key_get = "DetectorIds",
        detail_function = "get_detector", 
        join_key = "DetectorId", 
        detail_join_key = "DetectorId", 
        detail_get_key = "",
        pagination = True
    )
    
    """
    inventory['filters'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "guardduty", 
        aws_region = "all", 
        function_name = "list_members", 
        key_get = "",
        detail_function = "get_filter", 
        join_key = "FilterNames", 
        detail_join_key = "Name", 
        detail_get_key = "",
        pagination = True
    )
    """

    return inventory


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')
