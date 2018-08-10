# Python imports
import boto3
from botocore.exceptions import *
import botocore
import collections
import csv
import json

import smtplib
import os, hmac, hashlib, sys
import pprint
import logging
from sys import exit
import time

import res.utils as utils
import config

# AWS Services imports 
import res.compute as compute
import res.storage as storage
import res.db      as db
import res.glob    as glob
import res.iam     as iam
import res.network as net

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

# Argumentation
nb_arg = len(sys.argv) - 1
if (nb_arg == 0):
    arguments = config.SUPPORTED_COMMANDS
    nb_arg = len(arguments)
else:
    arguments = sys.argv[1:]
    utils.check_arguments(arguments)
print('-'*100)
print ('Number of arguments:', nb_arg, 'arguments.')
print ('Argument List:', str(arguments))
print('-'*100)

# 
# ----------------- EC2
#

if ('ec2' in arguments):
    ec2_inventory        = []
    interfaces_inventory = []
    vpcs_inventory       = []
    ebs_inventory        = []

    # Lookup in every AWS Region
    for current_region in regions:
    
        current_region_name = current_region['RegionName']
        utils.display(ownerId, current_region_name, "ec2 inventory")

        # EC2 instances
        instances = compute.get_ec2_inventory(current_region_name)
        for instance in instances:
            json_ec2_desc = json.loads(utils.json_datetime_converter(instance))
            ec2_inventory.append(compute.get_ec2_analysis(json_ec2_desc, current_region_name))

        # Network
        for ifc in compute.get_interfaces_inventory(current_region_name):
            interfaces_inventory.append(json.loads(utils.json_datetime_converter(ifc)))

        # VPCs
        for vpc in compute.get_vpc_inventory(current_region_name):
            vpcs_inventory.append(vpc)

        # EBS
        ebs_list = compute.get_ebs_inventory(current_region_name)
        for ebs in ebs_list:
            ebs_inventory.append(json.loads(utils.json_datetime_converter(ebs)))

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
if ('lambda' in arguments):
    utils.display(ownerId, "all regions", "lambda inventory")
    inventory["lambda"] = compute.get_lambda_inventory()


# 
# ----------------- Lighstail instances
#
if ('lightsail' in arguments):
    utils.display(ownerId, "all regions", "lightsail inventory")
    inventory['lightsail'] = json.loads(utils.json_datetime_converter(compute.get_lightsail_inventory()))


#
# ----------------- EFS inventory
#
if ('efs' in arguments):
    efs_inventory = []
    for current_region in regions:
        efs_list = storage.get_efs_inventory(ownerId, current_region['RegionName'])
        for efs in efs_list:
            efs_inventory.append(json.loads(utils.json_datetime_converter(efs)))
    inventory['efs'] = efs_inventory


#
# ----------------- Glacier inventory
#
if ('glacier' in arguments):
    glacier_inventory = []
    for current_region in regions:
        glacier_list = storage.get_glacier_inventory(ownerId, current_region['RegionName'])
        for glacier in glacier_list:
            glacier_inventory.append(json.loads(utils.json_datetime_converter(glacier)))
    inventory['glacier'] = glacier_inventory


#
# ----------------- RDS inventory
#
if ('rds' in arguments):
    rds_inventory = []
    for current_region in regions:
        current_region_name = current_region['RegionName']
        utils.display(ownerId, current_region_name, "rds inventory")
        rds_list = db.get_rds_inventory(ownerId, current_region_name)
        for rds in rds_list:
            rds_inventory.append(json.loads(utils.json_datetime_converter(rds)))
    inventory['rds'] = rds_inventory


#
# ----------------- dynamodb inventory
#
if ('dynamodb' in arguments):
    dynamodb_inventory = []
    for current_region in regions:
        current_region_name = current_region['RegionName']
        utils.display(ownerId, current_region_name, "dynamodb inventory")
        dynamodb_list = db.get_dynamodb_inventory(ownerId, current_region_name)
        for dynamodb in dynamodb_list:
            dynamodb_inventory.append(json.loads(utils.json_datetime_converter(dynamodb)))
    inventory['dynamodb'] = dynamodb_inventory


#
# ----------------- KMS inventory
#
if ('kms' in arguments):
    kms_inventory = []
    for current_region in regions:
        current_region_name = current_region['RegionName']
        utils.display(ownerId, current_region_name, "kms inventory")
        kms_list = iam.get_kms_inventory(ownerId, current_region_name)
        for kms in kms_list:
            kms_inventory.append(json.loads(utils.json_datetime_converter(kms)))
    inventory['kms'] = kms_inventory


#
# ----------------- API Gateway inventory
#
if ('apigateway' in arguments):
    apigateway_inventory = []
    for current_region in regions:
        current_region_name = current_region['RegionName']
        utils.display(ownerId, current_region_name, "apigateway inventory")
        apigateway_list = net.get_apigateway_inventory(ownerId, current_region_name)
        for apigateway in apigateway_list:
            apigateway_inventory.append(json.loads(utils.json_datetime_converter(apigateway)))
    inventory['apigateway'] = apigateway_inventory


#

#
# ----------------- Cost Explorer (experimental)
#
if ('ce' in arguments):
    ce_inventory = []
    utils.display(ownerId, 'global', "cost explorer inventory")
    list_ce = glob.get_ce_inventory(ownerId, None).get('ResultsByTime')
    for item in list_ce:
        ce_inventory.append(json.loads(utils.json_datetime_converter(item)))
    print(ce_inventory)
    inventory['ce'] = ce_inventory

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
if ('s3' in arguments):
    utils.display(ownerId, current_region_name, "S3 quick inventory")
    inventory["s3"] = storage.get_s3_inventory(current_region_name)

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

