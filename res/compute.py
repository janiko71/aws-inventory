import boto3
import botocore
import json
import config
import res.utils as utils
import res.glob  as glob

# to do : autoscaling, security groups
# =======================================================================================================================
#
#  Supported services   : EC2 (instances, EBS, Network interfaces, vpc), lambda, lightsail (full)
#  Unsupported services : EKS (not supported in SDK), Batch, Elastic Container Service (ECS), Elastic Beanstalk
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
        key_get = "Reservations",
        detail_function = "", 
        key_get_detail = "",
        key_selector = ""
    )


def get_ec2_analysis(instance, region_name):
    """
        Returns ec2 inventory with significant attributes only

        :param region: region name
        :type region: string

        :return: ec2 inventory
        :rtype: json
    """
    config.logger.info('ec2 inventory, region {}, get_ec2_analysis'.format(region_name))
    analysis = {}
    reservation_id = instance['ReservationId']
    groups = instance['Groups']
    for inst in instance.get('Instances'):
        analysis['Groups'] = groups
        analysis['RegionName'] = region_name
        analysis['ReservationId'] = reservation_id
        analysis['StateCode'] = inst.get('State').get('Code')
        analysis['StateName'] = inst.get('State').get('Name')
        analysis['InstanceId'] = inst.get('InstanceId')
        analysis['InstanceType'] = inst.get('InstanceType')
        analysis['LaunchTime'] = inst.get('LaunchTime')
        analysis['Architecture'] = inst.get('Architecture')
        analysis['Tenancy'] = inst.get('Placement').get('Tenancy')
        analysis['GroupName'] = inst.get('Placement').get('GroupName')
        analysis['AvailabilityZone'] = inst.get('Placement').get('AvailabilityZone')
        analysis['ImageId'] = inst.get('ImageId')
        analysis['VpcId'] = inst.get('VpcId')
        analysis['SubnetId'] = inst.get('SubnetId')
        analysis['SecurityGroups'] = inst.get('SecurityGroups')
        analysis['VirtualizationType'] = inst.get('VirtualizationType')
        analysis['PrivateIpAddress'] = inst.get('PrivateIpAddress')
        analysis['PrivateDnsName'] = inst.get('PrivateDnsName')
        analysis['PublicIpAddress'] = inst.get('PublicIpAddress')
        analysis['PublicDnsName'] = inst.get('PublicDnsName')
        analysis['KeyName'] = inst.get('KeyName')
        analysis['Hypervisor'] = inst.get('Hypervisor')
        analysis['VirtualizationType'] = inst.get('VirtualizationType')
        analysis['EbsOptimized'] = inst.get('EbsOptimized')
        analysis['Tags'] = []
        # tags
        try:
            for tag in inst.get('Tags'):
                analysis['Tags'].append(tag)
        except Exception:
            analysis['Tags'] = []
        analysis['RootDeviceType'] = inst.get('RootDeviceType')
        analysis['RootDeviceName'] = inst.get('RootDeviceName')

        # devices (disks). Only EBS ?
        disks = inst.get('BlockDeviceMappings')
        disks_list = []
        for disk in disks:
            device = {'DeviceName': disk['DeviceName'], 'VolumeId': disk['Ebs'].get('VolumeId'), 'Status': disk['Ebs'].get('Status')}
            disks_list.append(device)
        analysis['Devices'] = disks_list

        # Networking interfaces
        analysis['NetworkInterfaces'] = []
        interfaces = inst.get('NetworkInterfaces')
        for ifc in interfaces:
            desc_ifc = {
                'MacAddress': ifc['MacAddress'],
                'Status': ifc['Status'],
                'VpcId': ifc['VpcId'],
                'SubnetId': ifc['SubnetId'],
                'NetworkInterfaceId': ifc['NetworkInterfaceId'],
                'PrivateIpAddresses': ifc['PrivateIpAddresses'],
            }                
        analysis['NetworkInterfaces'].append(desc_ifc)

       
    return analysis


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
        key_get = "NetworkInterfaces",
        detail_function = "", 
        key_get_detail = "",
        key_selector = ""
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
        key_get = "Vpcs",
        detail_function = "", 
        key_get_detail = "",
        key_selector = ""
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
        key_get = "Volumes",
        detail_function = "", 
        key_get_detail = "",
        key_selector = ""
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
        key_get = "Environments",
        detail_function = "", 
        key_get_detail = "",
        key_selector = ""
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
        key_get = "Applications",
        detail_function = "", 
        key_get_detail = "",
        key_selector = ""
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
        key_get = "clusters",
        detail_function = "", 
        key_get_detail = "",
        key_selector = ""
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
        key_get_detail = "tasks",
        key_selector = "tasks"
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
        key_get = "Functions",
        detail_function = "", 
        key_get_detail = "",
        key_selector = ""
    )


#  ------------------------------------------------------------------------
#
#    Lightsail
#
#  ------------------------------------------------------------------------
def get_lightsail_inventory():
    """
        Returns lightsail inventory. 

        :return: lightsail inventory
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/lightsail.html
    """
    lightsail_inventory = {}
    region_name = 'all regions'
    config.logger.info('lightsail inventory, region {}, get_lightsail_inventory'.format(region_name))

    lightsail = boto3.client('lightsail')

    lightsail_instances_inventory = []
    lightsail_instances_list = lightsail.get_instances().get('instances')
    config.logger.info('lightsail instances inventory, region {}, get_lightsail_inventory'.format(region_name))
    for li in lightsail_instances_list:
        lightsail_instances_inventory.append(json.loads(utils.json_datetime_converter(li)))
    if (len(lightsail_instances_inventory) > 0):
        lightsail_inventory['lightsail-instances'] = lightsail_instances_inventory

    try:
        lb_inventory = []
        config.logger.info('lightsail Load Balancer inventory, region {}, get_lightsail_inventory'.format(region_name))
        lb_list = lightsail.get_load_balancers().get("loadBalancers")
        for lb in lb_list:
            lb_inventory.append(lb)
        if (len(lb_inventory) > 0):
            lightsail_inventory['lightsail-loadbalancers'] = lb_inventory
    except AttributeError:
        config.logger.error('lightsail Load Balancer inventory failed for region {}'.format(region_name))                    

    ip_inventory = []
    config.logger.info('lightsail IP inventory, region {}, get_lightsail_inventory'.format(region_name))
    ip_list = lightsail.get_static_ips().get('staticIps')
    for ip in ip_list:
        ip_inventory.append(ip)
    if (len(ip_inventory) > 0):
        lightsail_inventory['lightsail-ip'] = ip_inventory

    return lightsail_inventory



#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')