import boto3
import botocore
import json
import config
import res.utils as utils
import res.glob  as glob

'''
Supported services   : CloudFormation, CloudTrail, CloudWatch, AWS Auto Scaling 
Unsupported services : Config, OpsWork, Service Catalog, 
                       Systems Manager, Trusted Advisor, Managed Services
'''

def get_cloudformation_inventory(oId, profile, boto3_config, selected_regions):

    '''
        Returns cloudformation inventory (if the region is avalaible)

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: cloudformation inventory
        :rtype: json

        .. note:: https://boto3.readthedocs.io/en/latest/reference/services/cloudformation.html
    '''

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "cloudformation", 
        aws_region = "all", 
        function_name = "describe_stacks", 
        key_get = "Stacks",
        detail_function = "describe_stack_resources", 
        join_key = "StackName", 
        detail_join_key = "StackName", 
        detail_get_key = "",
        pagination = True
    )

def get_cloudtrail_inventory(oId, profile, boto3_config, selected_regions):

    '''
        Returns cloudtrail inventory (if the region is avalaible)

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: cloudtrail inventory
        :rtype: json

        .. note:: https://boto3.readthedocs.io/en/latest/reference/services/cloudtrail.html
    '''

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "cloudtrail", 
        aws_region = "all", 
        function_name = "describe_trails", 
        key_get = "trailList"
    )

def get_cloudwatch_inventory(oId, profile, boto3_config, selected_regions):

    '''
        Returns cloudwatch inventory (if the region is avalaible)

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: cloudwatch inventory
        :rtype: json

        .. note:: https://boto3.readthedocs.io/en/latest/reference/services/cloudwatch.html
    '''
    
    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "cloudwatch", 
        aws_region = "all", 
        function_name = "describe_alarms", 
        key_get = "MetricAlarms",
        pagination = True
    )

''' Hey, doc: we're in a module! '''

if (__name__ == '__main__'):
    print('Module => Do not execute')
