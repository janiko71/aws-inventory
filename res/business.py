import boto3
import botocore
import json
import config
import pprint, operator
import res.utils as utils
import res.glob as glob

# =======================================================================================================================
#
#  Supported services   : Alexa (very light), WorkMail
#  Unsupported services : Amazon Chime, WorkDocs
#
# =======================================================================================================================

#  ------------------------------------------------------------------------
#
#    Alexa for Business
#
#  ------------------------------------------------------------------------

def get_alexa_inventory(oId):
    """
        Returns alexa skills

        :param ownerId: ownerId (AWS account)
        :type ownerId: string

        :return: alexa skills inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/kms.html
    """ 
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "alexaforbusiness", 
        aws_region = "all", 
        function_name = "list_skills", 
        key_get = "SkillSummaries",
        detail_function = "describe_project", 
        join_key = "projectId", 
        detail_join_key = "id", 
        detail_get_key = ""
    )


#  ------------------------------------------------------------------------
#
#   WorkDocs
#
#  ------------------------------------------------------------------------

def get_workdocs_inventory(oId):
    """
        Returns workdocs inventory

        :param ownerId: ownerId (AWS account)
        :type ownerId: string

        :return: workdocs inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/kms.html
    """ 
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "workdocs", 
        aws_region = "all", 
        function_name = "???", 
        key_get = "???"
    )    


#  ------------------------------------------------------------------------
#
#   Workmail
#
#  ------------------------------------------------------------------------

def get_workmail_inventory(oId):
    """
        Returns workmail inventory

        :param ownerId: ownerId (AWS account)
        :type ownerId: string

        :return: workmail inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/kms.html
    """ 
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "workmail", 
        aws_region = "all", 
        function_name = "list_organizations" ,
        key_get = "OrganizationSummaries",
        detail_function = "describe_organization", 
        join_key = "OrganizationId", 
        detail_join_key = "OrganizationId", 
        detail_get_key = ""        
    )    


#
# Hey, doc: we're in a module!
#
#if (__name__ == '__main__'):
#    print('Module => Do not execute')