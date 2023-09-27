import boto3
import botocore
import json
import config
import res.utils as utils
import res.glob  as glob

# to do : security groups
# =======================================================================================================================
#
#  Supported services   : EC2 (instances, EBS, Network interfaces, vpc), lambda, lightsail (full), AWS Outposts,
#                           Elastic Container Service (ECS), Elastic Beanstalk, EKS, Batch, Serverless Application Repository
#  Unsupported services : EC2 Image Builder, App Runner
#
# =======================================================================================================================

#  ------------------------------------------------------------------------
#
#    EC2 
#
#  ------------------------------------------------------------------------

def get_ec2_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns ec2 inventory, without any analysis or any formatting

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: ec2 inventory
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/ec2.html
    """

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "ec2",
        aws_region = "all",
        function_name = "describe_instances",
        key_get = "Reservations",
        pagination = True
    )


def get_snapshot_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns snapshot inventory, without any analysis or any formatting

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: snapshot inventory
        :rtype: json

        .. note:: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_snapshots.html
    """

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "ec2",
        aws_region = "all",
        function_name = "describe_snapshots",
        key_get = "Snapshots",
        additional_parameters={'OwnerIds': [oId]}
    )


def get_interfaces_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns network interfaces detailed inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: network interfaces inventory
        :rtype: json
    """

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "ec2", 
        aws_region = "all", 
        function_name = "describe_network_interfaces", 
        key_get = "NetworkInterfaces"
    )


def get_vpc_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns VPC detailed inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: VPC inventory
        :rtype: json
    """

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "ec2", 
        aws_region = "all", 
        function_name = "describe_vpcs", 
        key_get = "Vpcs"
    )


def get_subnet_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns VPC subnets inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: VPC subnets inventory
        :rtype: json
    """

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "ec2", 
        aws_region = "all", 
        function_name = "describe_subnets", 
        key_get = "Subnets"
    )


def get_ebs_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns EBS detailed inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: EBS inventory
        :rtype: json
    """

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "ec2", 
        aws_region = "all", 
        function_name = "describe_volumes", 
        key_get = "Volumes",
        pagination = True
    )


def get_eips_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns Elastic IPs inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: Elastic IPs inventory
        :rtype: json
    """

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "ec2", 
        aws_region = "all", 
        function_name = "describe_addresses", 
        key_get = "Addresses"
    )


def get_egpus_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns Elastic GPUs inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: Elastic GPUs inventory
        :rtype: json
    """

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "ec2", 
        aws_region = "all", 
        function_name = "describe_elastic_gpus", 
        key_get = "ElasticGpuSet"
    )


def get_sg_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns Security Groups inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: Security Groups inventory
        :rtype: json
    """

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "ec2", 
        aws_region = "all", 
        function_name = "describe_security_groups", 
        key_get = "SecurityGroups",
        pagination = True
    )


def get_igw_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns Internet Gateways inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: Internet Gateways inventory
        :rtype: json
    """

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "ec2", 
        aws_region = "all", 
        function_name = "describe_internet_gateways", 
        key_get = "InternetGateways"
    )


def get_ngw_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns Nat Gateways inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: Nat Gateways inventory
        :rtype: json
    """

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
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

def get_elasticbeanstalk_environments_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns Elastic Beanstalk detailed inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: Elastic Beanstalk inventory (environments)
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/elasticbeanstalk.html
    """

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "elasticbeanstalk", 
        aws_region = "all", 
        function_name = "describe_environments", 
        key_get = "Environments"
    )


def get_elasticbeanstalk_applications_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns Elastic Beanstalk detailed inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: Elastic Beanstalk inventory (applications)
        :rtype: json
    """

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "elasticbeanstalk", 
        aws_region = "all", 
        function_name = "describe_applications", 
        key_get = "Applications"
    )



#  ------------------------------------------------------------------------
#
#    Autoscaling
#
#  ------------------------------------------------------------------------

def get_autoscaling_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns eks inventory (if the region is avalaible)

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: eks inventory
        :rtype: json

        .. note:: https://boto3.readthedocs.io/en/latest/reference/services/autoscaling.html
    """

    autoscaling_inventory = {}

    autoscaling_inventory['autoscaling-groups'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "autoscaling", 
        aws_region = "all", 
        function_name = "describe_auto_scaling_groups", 
        key_get = "AutoScalingGroups",
        pagination = True
    )

    autoscaling_inventory['autoscaling-launch-configuration'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "autoscaling", 
        aws_region = "all", 
        function_name = "describe_launch_configurations", 
        key_get = "LaunchConfigurations",
        pagination = True
    )

    autoscaling_inventory['autoscaling-plans'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
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

def get_lambda_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns lambda inventory.

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: lambda inventory
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/lambda.html
    """

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "lambda", 
        aws_region = "all", 
        function_name = "list_functions", 
        key_get = "Functions",
        pagination = True
    )


#  ------------------------------------------------------------------------
#
#    Serverless Application Repository
#
#  ------------------------------------------------------------------------

def get_serverlessrepo_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns serverlessrepo inventory.

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: serverlessrepo inventory
        :rtype: json

        .. note:: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/serverlessrepo.html
    """
    inventory = {}

    inventory = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "serverlessrepo", 
        aws_region = "all", 
        function_name = "list_applications", 
        key_get = "Applications",
        detail_function = "get_application", 
        join_key = "ApplicationId", 
        detail_join_key = "ApplicationId", 
        detail_get_key = "",
        pagination = True,
        pagination_detail = False        
    )


    return inventory
    

#  ------------------------------------------------------------------------
#
#    Batch
#
#  ------------------------------------------------------------------------

def get_batch_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns batch jobs inventory.

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: batch inventory
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/batch.html
    """
    inventory = {}

    inventory['job-definitions'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "batch", 
        aws_region = "all", 
        function_name = "describe_job_definitions", 
        key_get = "jobDefinitions"
    )

    inventory['job-queues'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "batch", 
        aws_region = "all", 
        function_name = "describe_job_queues", 
        key_get = "jobQueues"
    )

    inventory['compute-environments'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
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

def get_lightsail_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns lightsail inventory, with loadbalancers and IPs

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: lightsail inventory
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/lightsail.html
    """

    lightsail_inventory = {}

    lightsail_inventory['lightsail-instances'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "lightsail", 
        aws_region = "all", 
        function_name = "get_instances", 
        key_get = "instances",
        pagination = True
    )

    lightsail_inventory['lightsail-loadbalancers'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "lightsail", 
        aws_region = "all", 
        function_name = "get_load_balancers", 
        key_get = "loadBalancers"
    )

    lightsail_inventory['lightsail-ip'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "lightsail", 
        aws_region = "all", 
        function_name = "get_static_ips", 
        key_get = "staticIps"
    )

    lightsail_inventory['lightsail-disks'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "lightsail", 
        aws_region = "all", 
        function_name = "get_disks", 
        key_get = "disks"
    )    

    return lightsail_inventory


#  ------------------------------------------------------------------------
#
#    AWS Outposts
#
#  ------------------------------------------------------------------------

def get_outposts_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns lambda inventory.

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: lambda inventory
        :rtype: json

        .. note:: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/outposts.html
    """

    inventory = {}

    inventory['outposts'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "outposts", 
        aws_region = "all", 
        function_name = "list_outposts", 
        key_get = "Outposts",
        pagination = False,
        detail_get_key = "Outpost",
        detail_join_key = "OutpostId",
        pagination_detail = False
    )

    inventory['outposts_sites'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "outposts", 
        aws_region = "all", 
        function_name = "list_sites", 
        key_get = "Sites",
        pagination = False
    )

    return inventory

#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')