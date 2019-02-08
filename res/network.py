import boto3
import botocore
import json
import config
import res.utils as utils
import res.glob  as glob

# =======================================================================================================================
#
#  Supported services   : API Gateway (simple), VPC (in 'compute' module), Route 53, Cloud Front
#  Unsupported services : Direct Connect
#
# =======================================================================================================================


#  ------------------------------------------------------------------------
#
#    API Gateway (simple) 
#
#  ------------------------------------------------------------------------

def get_apigateway_inventory(oId):

    """
        Returns API Gateway inventory

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: API Gateway inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/apigateway.html
        ..todo:: add --> plans, api keys, custom domain names, client certificates, vpc links
    """
    
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "apigateway", 
        aws_region = "all", 
        function_name = "get_rest_apis", 
        key_get = "items",
        pagination = True
    )


#  ------------------------------------------------------------------------
#
#    CloudFront
#
#  ------------------------------------------------------------------------

def get_cloudfront_inventory(oId):

    """
        Returns cloudfront inventory

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: Cloudfront inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/cloudfront.html

    """
    
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "cloudfront", 
        aws_region = "all", 
        function_name = "list_distributions", 
        key_get = "Items",
        pagination = True
    )


#  ------------------------------------------------------------------------
#
#    Route 53
#
#  ------------------------------------------------------------------------

def get_route53_inventory(oId):

    """
        Returns route 53 inventory, partial.

        Traffic policies are not detailed because the detail function needs 2 arguments.

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: route 53 inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/route53.html

    """
    
    inventory = {}
    
    inventory['zones'] = glob.get_inventory(
        ownerId = oId,
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
        aws_service = "route53", 
        aws_region = "global", 
        function_name = "list_traffic_policies", 
        key_get = "TrafficPolicySummaries",
        pagination = True
    )

    inventory['domains'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "route53domains", 
        aws_region = "all", 
        function_name = "list_domains", 
        key_get = "Domains"
    )

    return inventory



#  ------------------------------------------------------------------------
#
#    Elastic Load Balancer
#
#  ------------------------------------------------------------------------

def get_elb_inventory(oId):

    """
        Returns ELB inventory

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: ELB inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/elb.html

    """

    return glob.get_inventory(
        ownerId = oId,
        aws_service = "elb",
        aws_region = "all",
        function_name = "describe_load_balancers",
        key_get = "LoadBalancerDescriptions",
        pagination = True
    )

#  ------------------------------------------------------------------------
#
#    Elastic Load Balancer v2
#
#  ------------------------------------------------------------------------

def get_elbv2_inventory(oId):

    """
        Returns ELBv2 inventory

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: ELBv2 inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/elbv2.html

    """
    
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "elbv2", 
        aws_region = "all", 
        function_name = "describe_load_balancers", 
        key_get = "LoadBalancers",
        pagination = True
    )

#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')