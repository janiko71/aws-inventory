import boto3
import botocore

def get_ec2_inventory(region):
    """
        Returns ec2 inventory, without any analysis or any formatting

        :param region: region name
        :type region: string

        :return: ec2 inventory
        :rtype: json

        .. note:: http://boto3.readthedocs.io/en/latest/reference/services/ec2.html
    """
    ec2 = boto3.client('ec2', region)
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


def get_interfaces_inventory(region):
    """
        Returns network interfaces detailed inventory

        :param region: region name
        :type region: string

        :return: network interfaces inventory
        :rtype: json
    """
    ec2 = boto3.client('ec2', region)
    inventory = []
    for ifc in ec2.describe_network_interfaces().get('NetworkInterfaces'):
        ifc['Region'] = region
        inventory.append(ifc)

    return inventory


def get_vpc_inventory(region):
    """
        Returns VPC detailed inventory

        :param region: region name
        :type region: string

        :return: VPC inventory
        :rtype: json
    """
    ec2 = boto3.client('ec2', region)
    inventory = []
    for vpc in ec2.describe_vpcs().get('Vpcs'):
        vpc['Region'] = region
        inventory.append(vpc)
    return inventory


def get_ebs_inventory(region):
    """
        Returns EBS detailed inventory

        :param region: region name
        :type region: string

        :return: EBS inventory
        :rtype: json
    """
    ec2 = boto3.client('ec2', region)
    inventory = []
    for ebs in ec2.describe_volumes().get('Volumes'):
        ebs['Region'] = region
        inventory.append(ebs)
    return inventory


# Hey, doc: we're in a module!
if (__name__ == '__main__'):
    print('Module => Do not execute')