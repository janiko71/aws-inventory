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
from time import gmtime, strftime

import res.internal_functions as internal

# AWS Services imports 
import res.ec2 as ec2
import res.s3 as s3
import res.eks as eks
import res.awslambda as awslambda


#
# Environment Variables & File handling & logging
#

# -- Some globals to initialize
def init_globals():
   
    global filepath
    global filename_json
    global logger

    # -- Some initial values
    ownerId = internal.get_ownerID()

    # --- Initial values for inventory files names
    t = gmtime()
    timestamp = strftime("%Y%m%d%H%M%S", t)
    filepath = './output/'
    filename_json = 'AWS_{}_{}.json'.format(ownerId, timestamp)

    # --- logging variables
    log_filepath    = './log/'
    logger          = logging.getLogger('aws-inventory')
    hdlr            = logging.FileHandler(log_filepath+'inventory.log')
    formatter       = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    # --- Log handler
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr) 
    logger.setLevel(logging.WARNING)

    # --- If needed: S3 bucket name to write inventory
    S3_INVENTORY_BUCKET="xx"

#
# Let's rock'n roll
#
init_globals()

# --- AWS basic information
ownerId = internal.get_ownerID()

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
    print('OwnerID : {}, EC2 inventory, Region : {}'.format(ownerId, current_region_name))

    # EC2 instances
    instances = ec2.get_ec2_inventory(current_region_name)
    for instance in instances:
       json_ec2_desc = json.loads(internal.json_datetime_converter(instance))
       ec2_inventory.append(ec2.get_ec2_analysis(json_ec2_desc, current_region_name))

    # Network
    for ifc in ec2.get_interfaces_inventory(current_region_name):
        interfaces_inventory.append(json.loads(internal.json_datetime_converter(ifc)))

    # VPCs
    vpcs_inventory.append(ec2.get_vpc_inventory(current_region_name))

    # EBS
    ebs_list = ec2.get_ebs_inventory(current_region_name)
    if len(ebs_list) > 0:
        ebs_inventory.append(json.loads(internal.json_datetime_converter(ebs_list)))

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
inventory["lambda"]        = awslambda.get_lambda_inventory(ownerId)


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

print('OwnerID : {}, S3 inventory, Region : {}'.format(ownerId, current_region_name))
inventory["s3"] = s3.get_s3_inventory(current_region_name)

#
# ----------------- Final inventory
#

try:
    json_file = open(filepath+filename_json,'w+')
except IOError as e:
    logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))

json_file.write(json.JSONEncoder().encode(inventory))

#
# EOF
#
json_file.close()

