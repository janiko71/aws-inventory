import boto3
import botocore
import json
import config
import pprint, operator
import res.utils as utils
import res.glob as glob

# =======================================================================================================================
#
#  Supported services   : CodeStar
#  Unsupported services : CodeCommit, CodeArtifact, CodeBuild, CodeDeploy, CodePipeline, Cloud9, X-Ray, AWS FIS
#  Not scriptable: CloudShell
#
# =======================================================================================================================

#  ------------------------------------------------------------------------
#
#    CodeStar
#
#  ------------------------------------------------------------------------

def get_codestar_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns codestar details

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: codestar inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/codestar.html
    """ 
    
    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "codestar", 
        aws_region = "all", 
        function_name = "list_projects", 
        key_get = "projects",
        detail_function = "describe_project", 
        join_key = "projectId", 
        detail_join_key = "id", 
        detail_get_key = ""
    )

#  ------------------------------------------------------------------------
#
#    CodeCommit
#
#  ------------------------------------------------------------------------

def get_codecommit_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns codecommit details

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: codecommit inventory
        :rtype: json

        ..note:: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/codecommit.html
    """ 
    
    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "codecommit", 
        aws_region = "all", 
        function_name = "list_repositories", 
        key_get = "repositories",
        pagination = True,
        detail_function = "describe_project", 
        join_key = "repositoryName", 
        detail_join_key = "repositoryName", 
        detail_get_key = "repositoryMetadata"
    )


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')