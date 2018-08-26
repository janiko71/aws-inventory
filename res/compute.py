import boto3
import botocore
import json
import config
import res.utils as utils
import res.glob  as glob

# to do : autoscaling, security groups
# =======================================================================================================================
#
#  Supported services   : EC2 (instances, EBS, Network interfaces, vpc), lambda, lightsail (full), 
#                           Elastic Container Service (ECS), Elastic Beanstalk, EKS, Batch
#  Unsupported services : None
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

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: ec2 inventory
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/ec2.html
    """
    
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "ec2", 
        aws_region = "all", 
        function_name = "describe_instances", 
        key_get = "Reservations",
        pagination = True
    )


def get_interfaces_inventory(oId):

    """
        Returns network interfaces detailed inventory

        :param oId: ownerId (AWS account)
        :type oId: string

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

        :param oId: ownerId (AWS account)
        :type oId: string

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


def get_subnet_inventory(oId):

    """
        Returns VPC subnets inventory

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: VPC subnets inventory
        :rtype: json
    """

    return glob.get_inventory(
        ownerId = oId,
        aws_service = "ec2", 
        aws_region = "all", 
        function_name = "describe_subnets", 
        key_get = "Subnets"
    )


def get_ebs_inventory(oId):

    """
        Returns EBS detailed inventory

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: EBS inventory
        :rtype: json
    """

    return glob.get_inventory(
        ownerId = oId,
        aws_service = "ec2", 
        aws_region = "all", 
        function_name = "describe_volumes", 
        key_get = "Volumes",
        pagination = True
    )


def get_eips_inventory(oId):

    """
        Returns Elastic IPs inventory

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: Elastic IPs inventory
        :rtype: json
    """

    return glob.get_inventory(
        ownerId = oId,
        aws_service = "ec2", 
        aws_region = "all", 
        function_name = "describe_addresses", 
        key_get = "Addresses"
    )


def get_egpus_inventory(oId):

    """
        Returns Elastic GPUs inventory

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: Elastic GPUs inventory
        :rtype: json
    """

    return glob.get_inventory(
        ownerId = oId,
        aws_service = "ec2", 
        aws_region = "all", 
        function_name = "describe_elastic_gpus", 
        key_get = "ElasticGpuSet"
    )


def get_sg_inventory(oId):

    """
        Returns Security Groups inventory

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: Security Groups inventory
        :rtype: json
    """

    return glob.get_inventory(
        ownerId = oId,
        aws_service = "ec2", 
        aws_region = "all", 
        function_name = "describe_security_groups", 
        key_get = "SecurityGroups",
        pagination = True
    )


def get_igw_inventory(oId):

    """
        Returns Internet Gateways inventory

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: Internet Gateways inventory
        :rtype: json
    """

    return glob.get_inventory(
        ownerId = oId,
        aws_service = "ec2", 
        aws_region = "all", 
        function_name = "describe_internet_gateways", 
        key_get = "InternetGateways"
    )


def get_ngw_inventory(oId):

    """
        Returns Nat Gateways inventory

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: Nat Gateways inventory
        :rtype: json
    """

    return glob.get_inventory(
        ownerId = oId,
        aws_service = "ec2", 
        aws_region = "all", 
        function_name = "describe_nat_gateways", 
        key_get = "NatGateways"
    )


#  ------------------------------------------------------------------------
#
#    Elastic Beanstalk 
#
#  ------------------------------------------------------------------------

def get_elasticbeanstalk_environments_inventory(oId):

    """
        Returns Elastic Beanstalk detailed inventory

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: Elastic Beanstalk inventory (environments)
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/elasticbeanstalk.html
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

        :param oId: ownerId (AWS account)
        :type oId: string

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

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: ECS inventory
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/ecs.html
    """

    return glob.get_inventory(
        ownerId = oId,
        aws_service = "ecs", 
        aws_region = "all", 
        function_name = "describe_clusters", 
        key_get = "clusters"
    )
    #detail_function = "list_container_instances",
    #join_key = "clusterName", 
    #detail_join_key = "cluster", 
    #detail_get_key = ""
    

def get_ecs_services_inventory(oId):

    """
        Returns ECS tasks inventory  NOT WORKING YET

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: ECS tasks inventory
        :rtype: json
    """

    return glob.get_inventory(
        ownerId = oId,
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
    

def get_ecs_tasks_inventory(oId):

    """
        Returns ECS tasks inventory

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: ECS tasks inventory
        :rtype: json
    """

    return glob.get_inventory(
        ownerId = oId,
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

def get_eks_inventory(oId):

    """
        Returns eks inventory (if the region is avalaible)

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: eks inventory
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/eks.html
    """

    inv = glob.get_inventory(
        ownerId = oId,
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
#    Autoscaling
#
#  ------------------------------------------------------------------------

def get_autoscaling_inventory(oId):

    """
        Returns eks inventory (if the region is avalaible)

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: eks inventory
        :rtype: json

        .. note:: https://boto3.readthedocs.io/en/latest/reference/services/autoscaling.html
    """

    autoscaling_inventory = {}

    autoscaling_inventory['autoscaling-groups'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "autoscaling", 
        aws_region = "all", 
        function_name = "describe_auto_scaling_groups", 
        key_get = "AutoScalingGroups",
        pagination = True
    )

    autoscaling_inventory['autoscaling-launch-configuration'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "autoscaling", 
        aws_region = "all", 
        function_name = "describe_launch_configurations", 
        key_get = "LaunchConfigurations",
        pagination = True
    )

    autoscaling_inventory['autoscaling-plans'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "autoscaling-plans", 
        aws_region = "all", 
        function_name = "describe_scaling_plans", 
        key_get = "ScalingPlans"
    )

    return autoscaling_inventory


#  ------------------------------------------------------------------------
#
#    Lambda
#
#  ------------------------------------------------------------------------

def get_lambda_inventory(oId):

    """
        Returns lambda inventory.

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: lambda inventory
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/lambda.html
    """

    return glob.get_inventory(
        ownerId = oId,
        aws_service = "lambda", 
        aws_region = "all", 
        function_name = "list_functions", 
        key_get = "Functions",
        pagination = True
    )


#  ------------------------------------------------------------------------
#
#    Batch
#
#  ------------------------------------------------------------------------

def get_batch_inventory(oId):

    """
        Returns batch jobs inventory.

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: batch inventory
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/batch.html
    """
    inventory = {}

    inventory['job-definitions'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "batch", 
        aws_region = "all", 
        function_name = "describe_job_definitions", 
        key_get = "jobDefinitions"
    )

    inventory['job-queues'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "batch", 
        aws_region = "all", 
        function_name = "describe_job_queues", 
        key_get = "jobQueues"
    )

    inventory['compute-environements'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "batch", 
        aws_region = "all", 
        function_name = "describe_compute_environments", 
        key_get = "computeEnvironments"
    )

    return inventory



#  ------------------------------------------------------------------------
#
#    Lightsail
#
#  ------------------------------------------------------------------------

def get_lightsail_inventory(oId):

    """
        Returns lightsail inventory, with loadbalancers and IPs

        :param oId: ownerId (AWS account)
        :type oId: string

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
        key_get = "instances",
        pagination = True
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

    lightsail_inventory['lightsail-disks'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "lightsail", 
        aws_region = "all", 
        function_name = "get_disks", 
        key_get = "disks"
    )    

    return lightsail_inventory


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')