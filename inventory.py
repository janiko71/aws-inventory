# Python imports
import boto3
from botocore.exceptions import ClientError
import botocore
import collections
import csv
import json

import smtplib
import os, hmac, hashlib
import pprint
import logging
from sys import exit
import time

import res.utils as utils
import config

# AWS Services imports 
import res.compute as compute
import res.s3 as s3

#
#  Useful local functions
#
def display(ownerId, function, region_name):
    print(config.display.format(ownerId, function, region_name))
    return


#
# Let's rock'n roll
#

# --- AWS basic information
ownerId = utils.get_ownerID()
config.logger.info('OWNER ID:'+ownerId)


# --- AWS Regions 
with open('aws_regions.json') as json_file:
    aws_regions = json.load(json_file)
regions = aws_regions.get('Regions',[] ) 


# Initialization
inventory = {}

# 
# ----------------- EC2
#

ec2_inventory        = []
interfaces_inventory = []
vpcs_inventory       = []
ebs_inventory        = []

# Lookup in every AWS Region
for current_region in regions:
   
    current_region_name = current_region['RegionName']
    display(ownerId, current_region_name, "ec2 inventory")

    # EC2 instances
    instances = compute.get_ec2_inventory(current_region_name)
    for instance in instances:
       json_ec2_desc = json.loads(utils.json_datetime_converter(instance))
       ec2_inventory.append(compute.get_ec2_analysis(json_ec2_desc, current_region_name))

    # Network
    for ifc in compute.get_interfaces_inventory(current_region_name):
        interfaces_inventory.append(json.loads(utils.json_datetime_converter(ifc)))

    # VPCs
    vpcs_inventory.append(compute.get_vpc_inventory(current_region_name))

    # EBS
    ebs_list = compute.get_ebs_inventory(current_region_name)
    if len(ebs_list) > 0:
        ebs_inventory.append(json.loads(utils.json_datetime_converter(ebs_list)))

    # EBS, snapshot
    # describe_nat_gateways()
    # describe_internet_gateways()
    # describe_reserved_instances()
    # describe_snapshots()
    # describe_subnets()

inventory["ec2"]            = ec2_inventory
inventory["ec2-interfaces"] = interfaces_inventory
inventory["ec2-vpcs"]       = vpcs_inventory
inventory["ec2-ebs"]        = ebs_inventory

# 
# ----------------- Lambda functions
#
display(ownerId, "all regions", "lambda inventory")
inventory["lambda"] = compute.get_lambda_inventory()

# 
# ----------------- Lighstail instances
#
display(ownerId, "all regions", "lightsail inventory")
inventory["lightsail"] = compute.get_lightsail_inventory()


#
# ----------------- EKS inventory (Kubernetes) : not implemented yet in AWS SDK
#
#for current_region in regions:
#    current_region_name = current_region['RegionName']
#    eks_list = eks.get_eks_inventory(ownerId, current_region_name)
#    #print(eks_list)
# Other non implemented services:
#  - alexaforbusiness


#
# International Resources (no region)
#

current_region_name = 'global'

#
# ----------------- S3 quick inventory
#
display(ownerId, current_region_name, "S3 quick inventory")
inventory["s3"] = s3.get_s3_inventory(current_region_name)

#
# ----------------- Final inventory
#

filename_json = 'AWS_{}_{}.json'.format(ownerId, config.timestamp)
try:
    json_file = open(config.filepath+filename_json,'w+')
except IOError as e:
    config.logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))

json_file.write(json.JSONEncoder().encode(inventory))

#
# EOF
#
json_file.close()

