import boto3
import botocore

def get_ebs_inventory(region):
    ec2 = boto3.client('ec2', region)
    inventory = ec2.describe_instances().get('Reservations')
    return inventory

if (__name__ == '__main__'):
    print('Module => Do not execute')