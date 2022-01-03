import boto3
import botocore
import json
import config
import res.utils as utils
import res.glob  as glob

'''
    Supported services   : API Gateway (simple), VPC (in 'compute' module), Route 53, CloudFront
    Unsupported services : Direct Connect, AWS App Mesh, AWS Cloud Map, Global Accelerator
'''

def get_apigateway_inventory(oId, profile, boto3_config, selected_regions):

    '''
        Returns API Gateway inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: API Gateway inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/apigateway.html
        ..todo:: add --> plans, api keys, custom domain names, client certificates, vpc links
    '''
    
    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "apigateway", 
        aws_region = "all", 
        function_name = "get_rest_apis", 
        key_get = "items",
        pagination = True
    )

def get_apigatewayv2_inventory(oId, profile, boto3_config, selected_regions):

    '''
        Returns API Gateway inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: API Gateway inventory
        :rtype: json

        ..note:: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/apigatewayv2.html
        ..todo:: add --> plans, api keys, custom domain names, client certificates, vpc links
    '''
    
    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "apigatewayv2", 
        aws_region = "all", 
        function_name = "get_apis", 
        key_get = "Items",
        pagination = True
    )

def get_cloudfront_inventory(oId, profile, boto3_config, selected_regions):

    '''
        Returns cloudfront inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: Cloudfront inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/cloudfront.html

    '''
    
    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "cloudfront", 
        aws_region = "global", 
        function_name = "list_distributions", 
        key_get = "Items",
        #key_get = "DistributionList",
        pagination = True
    )

def get_route53_inventory(oId, profile, boto3_config, selected_regions):

    '''
        Returns route 53 inventory, partial.

        Traffic policies are not detailed because the detail function needs 2 arguments.

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: route 53 inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/route53.html

    '''
    
    inventory = {}
    
    inventory['zones'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "route53", 
        aws_region = "global", 
        function_name = "list_hosted_zones_by_name", 
        key_get = "HostedZones",
        detail_function = "list_resource_record_sets", 
        join_key = "Id", 
        detail_join_key = "HostedZoneId", 
        detail_get_key = "ResourceRecordSets",
        pagination = True
    )

    inventory['traffic-policies'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "route53", 
        aws_region = "global", 
        function_name = "list_traffic_policies", 
        key_get = "TrafficPolicySummaries",
        pagination = True
    )

    inventory['domains'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "route53domains", 
        aws_region = "all", 
        function_name = "list_domains", 
        key_get = "Domains"
    )

    return inventory

def get_elb_inventory(oId, profile, boto3_config, selected_regions):

    '''
        Returns ELB inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: ELB inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/elb.html

    '''

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "elb",
        aws_region = "all",
        function_name = "describe_load_balancers",
        key_get = "LoadBalancerDescriptions",
        pagination = True
    )

def get_elbv2_inventory(oId, profile, boto3_config, selected_regions):

    '''
        Returns ELBv2 inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: ELBv2 inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/elbv2.html

    '''
    
    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "elbv2", 
        aws_region = "all", 
        function_name = "describe_load_balancers", 
        key_get = "LoadBalancers",
        pagination = True
    )

''' Hey, doc: we're in a module! '''

if (__name__ == '__main__'):
    print('Module => Do not execute')
