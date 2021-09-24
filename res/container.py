import boto3
import botocore
import json
import config
import res.utils as utils
import res.glob  as glob

# =======================================================================================================================
#
#  Supported services   : EKS, Elastic Container Service, Elastic Container Registry
#  Unsupported services : Red Hat Openshift
#
# =======================================================================================================================

#  ------------------------------------------------------------------------
#
#    EC2 Container Service (ECS)
#
#  ------------------------------------------------------------------------

def get_ecs_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns ECS detailed inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: ECS inventory
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/ecs.html
    """

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "ecs", 
        aws_region = "all", 
        function_name = "describe_clusters", 
        key_get = "clusters"
    )
    #detail_function = "list_container_instances",
    #join_key = "clusterName", 
    #detail_join_key = "cluster", 
    #detail_get_key = ""
    

def get_ecs_services_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns ECS tasks inventory  NOT WORKING YET

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: ECS tasks inventory
        :rtype: json
    """

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "ecs", 
        aws_region = "all", 
        function_name = "list_services", 
        key_get = "serviceArns",
        detail_function = "describe_services", 
        join_key = "", 
        detail_join_key = "services", 
        detail_get_key = "services",
        pagination = True,
        pagination_detail = True
    )
    

def get_ecs_tasks_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns ECS tasks inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: ECS tasks inventory
        :rtype: json
    """

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "ecs", 
        aws_region = "all", 
        function_name = "list_task_definitions", 
        key_get = "taskDefinitionArns",
        detail_function = "describe_task_definition", 
        join_key = "taskDefinitionArn", 
        detail_join_key = "taskDefinition", 
        detail_get_key = "taskDefinition",
        pagination = True,
        pagination_detail = True
    )


#  ------------------------------------------------------------------------
#
#    EKS
#
#  ------------------------------------------------------------------------

def get_eks_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns eks inventory (if the region is avalaible)

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: eks inventory
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/eks.html
    """

    inv = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "eks", 
        aws_region = "all", 
        function_name = "list_clusters", 
        key_get = "clusters",
        detail_function = "describe_cluster", 
        join_key = "", 
        detail_join_key = "name", 
        detail_get_key = "cluster"
    )
    return inv


#  ------------------------------------------------------------------------
#
#    ECR
#
#  ------------------------------------------------------------------------

def get_ecr_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns elastic container registry inventory (if the region is avalaible)

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: eks inventory
        :rtype: json

        .. note:: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr.html
    """

    # Special loop here

    inventory = {}

    desc_repo_list =  glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "ecr", 
        aws_region = "all", 
        function_name = "describe_repositories", 
        key_get = "repositories"
    )

    # Not very handy: we have to disrupt our method

    images_list = {}
    
    for repo in desc_repo_list:

        inventory[repo['repositoryName']] = {
            'repositoryArn': repo['repositoryName'],
            'registryId': repo['registryId'],
            'repositoryName': repo['repositoryName'],
            'RegionName': repo['RegionName'],
            'repositoryUri': repo['repositoryUri'],
            'createdAt': repo['createdAt'],
            'imageTagMutability': repo['imageTagMutability'],
            'imageScanningConfiguration': repo['imageScanningConfiguration'],
            'encryptionConfiguration': repo['encryptionConfiguration'],
            'imagesList': {}
            }

        inventory[repo['repositoryName']]['imagesList'] = glob.get_inventory(
            ownerId = oId,
            profile = profile,
            boto3_config = boto3_config,
            selected_regions = repo['RegionName'],
            aws_service = "ecr", 
            aws_region = "all", 
            function_name = "list_images", 
            key_get = "imageIds",
            additional_parameters = {'repositoryName': repo['repositoryName']},
            detail_function = "describe_images",
            join_key = "imageIds", 
            detail_join_key = "imageIds", 
            detail_get_key = "imageDetails",
            pagination_detail = True
        )

    return inventory


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')