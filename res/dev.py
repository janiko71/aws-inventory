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
#  Unsupported services : CodeCommit, CodeArtifact, CodeBuild, CodeDeploy, CodePipeline, Cloud9, CloudShell, X-Ray, AWS FIS
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


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')