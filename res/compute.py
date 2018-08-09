import boto3
import botocore
import json
import config
import res.utils as utils


#  ------------------------------------------------------------------------
#
#    EC2 
#
#  ------------------------------------------------------------------------

def get_ec2_inventory(region_name):
    """
        Returns ec2 inventory, without any analysis or any formatting

        :param region_name: region name
        :type region_name: string

        :return: ec2 inventory
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/ec2.html
    """
    ec2 = boto3.client('ec2', region_name)
    config.logger.info('ec2 inventory, region {}, get_ec2_inventory'.format(region_name))
    inventory = ec2.describe_instances().get('Reservations')
    return inventory


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
        analysis['Region'] = region_name
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


def get_interfaces_inventory(region_name):
    """
        Returns network interfaces detailed inventory

        :param region: region name
        :type region: string

        :return: network interfaces inventory
        :rtype: json
    """
    config.logger.info('ec2 inventory, region {}, get_interfaces_inventory'.format(region_name))
    ec2 = boto3.client('ec2', region_name)
    inventory = []
    for ifc in ec2.describe_network_interfaces().get('NetworkInterfaces'):
        ifc['Region'] = region_name
        inventory.append(ifc)

    return inventory


def get_vpc_inventory(region_name):
    """
        Returns VPC detailed inventory

        :param region: region name
        :type region: string

        :return: VPC inventory
        :rtype: json
    """
    config.logger.info('ec2 inventory, region {}, get_vpc_inventory'.format(region_name))
    ec2 = boto3.client('ec2', region_name)
    inventory = []
    for vpc in ec2.describe_vpcs().get('Vpcs'):
        vpc['Region'] = region_name
        inventory.append(vpc)
    return inventory


def get_ebs_inventory(region_name):
    """
        Returns EBS detailed inventory

        :param region: region name
        :type region: string

        :return: EBS inventory
        :rtype: json
    """
    config.logger.info('ec2 inventory, region {}, get_vpc_inventory'.format(region_name))
    ec2 = boto3.client('ec2', region_name)
    inventory = []
    for ebs in ec2.describe_volumes().get('Volumes'):
        ebs['Region'] = region_name
        inventory.append(ebs)
    return inventory


#  ------------------------------------------------------------------------
#
#    EKS
#
#  ------------------------------------------------------------------------

def get_eks_inventory(ownerId, region_name):
    """
        Returns eks inventory (if the region is avalaible)

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

def get_lambda_inventory():
    """
        Returns lambda inventory.

        :return: S3 inventory
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/lambda.html
    """
    config.logger.info('lambda inventory, region {}, get_lambda_inventory'.format('all regions'))
    awslambda = boto3.client('lambda')
    lambda_list = awslambda.list_functions().get('Functions')
   
    return lambda_list


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

    lb_inventory = []
    config.logger.info('lightsail Load Balancer inventory, region {}, get_lightsail_inventory'.format(region_name))
    lb_list = lightsail.get_load_balancers().get("loadBalancers")
    for lb in lb_list:
        lb_inventory.append(lb)
    if (len(lb_inventory) > 0):
        lightsail_inventory['lightsail-loadbalancers'] = lb_inventory

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