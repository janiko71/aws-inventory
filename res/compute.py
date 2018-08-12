import boto3
import botocore
import json
import config
import res.utils as utils
import res.glob  as glob

# to do : autoscaling, security groups
# =======================================================================================================================
#
#  Supported services   : EC2 (instances, EBS, Network interfaces, vpc), lambda, lightsail (full), Elastic Container Service (ECS), Elastic Beanstalk
#  Unsupported services : EKS (not supported in SDK), Batch
#
# =======================================================================================================================

#  ------------------------------------------------------------------------
#
#    EC2 
#
#  ------------------------------------------------------------------------

def get_ec2_inventory(oId):
    """
        Returns ec2 inventory, without any analysis or any formatting

        :param region_name: region name
        :type region_name: string

        :return: ec2 inventory
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/ec2.html
    """
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "ec2", 
        aws_region = "all", 
        function_name = "describe_instances", 
        key_get = "Reservations"
    )


def get_interfaces_inventory(oId):
    """
        Returns network interfaces detailed inventory

        :param region: region name
        :type region: string

        :return: network interfaces inventory
        :rtype: json
    """
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "ec2", 
        aws_region = "all", 
        function_name = "describe_network_interfaces", 
        key_get = "NetworkInterfaces"
    )


def get_vpc_inventory(oId):
    """
        Returns VPC detailed inventory

        :param region: region name
        :type region: string

        :return: VPC inventory
        :rtype: json
    """
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "ec2", 
        aws_region = "all", 
        function_name = "describe_vpcs", 
        key_get = "Vpcs"
    )


def get_ebs_inventory(oId):
    """
        Returns EBS detailed inventory

        :param region: region name
        :type region: string

        :return: EBS inventory
        :rtype: json
    """
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "ec2", 
        aws_region = "all", 
        function_name = "describe_volumes", 
        key_get = "Volumes"
    )


#  ------------------------------------------------------------------------
#
#    Elastic Beanstalk /!\ Not sure it works well (often returns empty responses!!!)
#
#  ------------------------------------------------------------------------

def get_elasticbeanstalk_environments_inventory(oId):
    """
        Returns Elastic Beanstalk detailed inventory

        :param region: region name
        :type region: string

        :return: Elastic Beanstalk inventory (environments)
        :rtype: json
    """
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "elasticbeanstalk", 
        aws_region = "all", 
        function_name = "describe_environments", 
        key_get = "Environments"
    )


def get_elasticbeanstalk_applications_inventory(oId):
    """
        Returns Elastic Beanstalk detailed inventory

        :param region: region name
        :type region: string

        :return: Elastic Beanstalk inventory (applications)
        :rtype: json
    """
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "elasticbeanstalk", 
        aws_region = "all", 
        function_name = "describe_applications", 
        key_get = "Applications"
    )


#  ------------------------------------------------------------------------
#
#    EC2 Container Service (ECS)
#
#  ------------------------------------------------------------------------

def get_ecs_inventory(oId):
    """
        Returns ECS detailed inventory

        :param region: region name
        :type region: string

        :return: ECS inventory
        :rtype: json
    """
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "ecs", 
        aws_region = "all", 
        function_name = "describe_clusters", 
        key_get = "clusters"
    )

def get_ecs_tasks_inventory(oId):
    """
        Returns ECS tasks inventory /!\ NOT WORKING YET

        :param region: region name
        :type region: string

        :return: ECS inventory
        :rtype: json
    """
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "ecs", 
        aws_region = "all", 
        function_name = "list_tasks", 
        key_get = "taskArns",
        detail_function = "describe_tasks", 
        join_key = "tasks", 
        detail_join_key = "tasks", 
        detail_get_key = "tasks"
    )


#  ------------------------------------------------------------------------
#
#    EKS
#
#  ------------------------------------------------------------------------

def get_eks_inventory(ownerId, region_name):
    """
        Returns eks inventory (if the region is avalaible)

        :param ownerId: ownerId (AWS account)
        :type ownerId: string
        :param region: region name
        :type region: string

        :return: S3 inventory
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/eks.html
    """
    inventory = []
    try:
        eks = boto3.client('eks')
        print('OwnerID : {}, EKS inventory, Region : {}'.format(ownerId, region_name))
        inventory.append(eks.list_clusters())
    except:
        print('OwnerID : {}, EKS not supported in region : {}'.format(ownerId, region_name))
    
    return inventory


#  ------------------------------------------------------------------------
#
#    Lambda
#
#  ------------------------------------------------------------------------

def get_lambda_inventory(oId):
    """
        Returns lambda inventory.

        :return: S3 inventory
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/lambda.html
    """
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "lambda", 
        aws_region = "all", 
        function_name = "list_functions", 
        key_get = "Functions"
    )


#  ------------------------------------------------------------------------
#
#    Lightsail
#
#  ------------------------------------------------------------------------
def get_lightsail_inventory(oId):
    """
        Returns lightsail inventory. 

        :return: lightsail inventory
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/lightsail.html
    """
    lightsail_inventory = {}

    lightsail_inventory['lightsail-instances'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "lightsail", 
        aws_region = "all", 
        function_name = "get_instances", 
        key_get = "instances"
    )

    lightsail_inventory['lightsail-loadbalancers'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "lightsail", 
        aws_region = "all", 
        function_name = "get_load_balancers", 
        key_get = "loadBalancers"
    )

    lightsail_inventory['lightsail-ip'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "lightsail", 
        aws_region = "all", 
        function_name = "get_static_ips", 
        key_get = "staticIps"
    )

    return lightsail_inventory


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')