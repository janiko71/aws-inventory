import boto3
import botocore
import json
import config
import pprint, operator
import res.utils as utils
import res.glob as glob

"""
    Supported services   : Alexa (very light), WorkMail
    Unsupported services : Amazon Chime, WorkDocs
"""
def get_alexa_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns alexa skills

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: alexa skills inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/alexaforbusiness.html
    """ 
    
    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "alexaforbusiness", 
        aws_region = "all", 
        function_name = "list_skills", 
        key_get = "SkillSummaries",
        detail_function = "describe_project", 
        join_key = "projectId", 
        detail_join_key = "id", 
        detail_get_key = "",
        pagination = True
    )

def get_workdocs_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns workdocs inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string
        
        :return: workdocs inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/workdocs.html
    """ 

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "workdocs", 
        aws_region = "all", 
        function_name = "???", 
        key_get = "???"
    )    

def get_workmail_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns workmail inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: workmail inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/workmail.html
    """ 

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "workmail", 
        aws_region = "all", 
        function_name = "list_organizations" ,
        key_get = "OrganizationSummaries",
        detail_function = "describe_organization", 
        join_key = "OrganizationId", 
        detail_join_key = "OrganizationId", 
        detail_get_key = ""  ,
        pagination = True  
    )    



''' Hey, doc: we're in a module! '''

if (__name__ == '__main__'):
    print('Module => Do not execute')
