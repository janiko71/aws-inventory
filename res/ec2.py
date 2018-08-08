import boto3
import botocore

def get_ec2_inventory(region):
    ec2 = boto3.client('ec2', region)
    inventory = ec2.describe_instances().get('Reservations')
    return inventory

def get_ec2_analysis(instance):
    analysis = {}
    reservation_id = instance['ReservationId']
    groups = instance['Groups']
    for inst in instance.get('Instances'):
        analysis['Groups'] = groups
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
            device = (disk['DeviceName'], disk['Ebs'].get('VolumeId'), disk['Ebs'].get('Status'))
            disks_list.append(device)
        analysis['Devices'] = disks_list
        '''
        analysis['InstanceId'] = inst.get('InstanceId')
        analysis['InstanceId'] = inst.get('InstanceId')
        analysis['InstanceId'] = inst.get('InstanceId')
        analysis['InstanceId'] = inst.get('InstanceId')
        analysis['InstanceId'] = inst.get('InstanceId')
        analysis['InstanceId'] = inst.get('InstanceId')
        analysis['InstanceId'] = inst.get('InstanceId')
        '''

    print(analysis)


if (__name__ == '__main__'):
    print('Module => Do not execute')