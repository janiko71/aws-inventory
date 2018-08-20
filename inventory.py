# Python imports
import boto3
from botocore.exceptions import EndpointConnectionError, ClientError
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
import res.glob       as glob
import res.compute    as compute
import res.storage    as storage
import res.db         as db
import res.dev        as dev
import res.iam        as iam
import res.network    as net
import res.fact       as fact
import res.security   as security
import res.management as mgn
import res.business   as bus


# --- AWS basic information

ownerId = utils.get_ownerID()
config.logger.info('OWNER ID:'+ownerId)


# --- AWS Regions 

with open('aws_regions.json') as json_file:
    aws_regions = json.load(json_file)
regions = aws_regions.get('Regions',[] ) 


# --- Inventory initialization

inventory = {}

# --- Argumentation. See function check_arguments.
# 
# If we find log level parameter, we adjust log level.
# If we find no service name, we inventory all services.
# Else we only inventory services passed in cmd line.

arguments = utils.check_arguments(sys.argv[1:])
nb_arg = len(arguments)

# if no arguments, we try all AWS services
if (nb_arg == 0):
    arguments = config.SUPPORTED_COMMANDS
    arguments.remove('ce')  # For it's not free, cost explorer is removed from defaults inventory. You need to call it explicitly.

# --- Displaying execution parameters
print('-'*100)
print ('Number of services:', len(arguments))
print ('Services List     :', str(arguments))
print('-'*100)

# --- Progression counter initialization

config.nb_units_done = 0
for svc in arguments:
    config.nb_units_todo += (config.nb_regions * config.SUPPORTED_INVENTORIES[svc])


#
# Let's rock'n roll
#


#################################################################
#                           COMPUTE                             #
#################################################################
# 
# ----------------- EC2
#

if ('ec2' in arguments):
    inventory["ec2"] = compute.get_ec2_inventory(ownerId)
    inventory["ec2-network-interfaces"] = compute.get_interfaces_inventory(ownerId)
    inventory["ec2-vpcs"] = compute.get_vpc_inventory(ownerId)
    inventory["ec2-ebs"] = compute.get_ebs_inventory(ownerId)

# 
# ----------------- Lambda functions
#
if ('lambda' in arguments):
    inventory["lambda"] = compute.get_lambda_inventory(ownerId)

# 
# ----------------- Elastic beanstalk
#
if ('elasticbeanstalk' in arguments):
    inventory["elasticbeanstalk"] = {
        "elasticbeanstalk-environments": compute.get_elasticbeanstalk_environments_inventory(ownerId),
        "elasticbeanstalk-applications": compute.get_elasticbeanstalk_applications_inventory(ownerId)
    }

# 
# ----------------- ECS
#
if ('ecs' in arguments):
    inventory["ecs"] = {
        "ecs-clusters": compute.get_ecs_inventory(ownerId),
        "ecs-tasks": compute.get_ecs_tasks_inventory(ownerId)
    }        

# 
# ----------------- Lighstail instances
#
if ('lightsail' in arguments):
    inventory['lightsail'] = compute.get_lightsail_inventory(ownerId)

# 
# ----------------- Autoscaling
#
if ('autoscaling' in arguments):
    inventory['autoscaling'] = compute.get_autoscaling_inventory(ownerId)

#
# ----------------- EKS inventory
#
if ('eks' in arguments):
    inventory['eks'] = compute.get_eks_inventory(ownerId)

#
# ----------------- Batch jobs inventory
#
if ('batch' in arguments):
    inventory['batch'] = compute.get_batch_inventory(ownerId)


#################################################################
#                           STORAGE                             #
#################################################################
#
# ----------------- EFS inventory
#
if ('efs' in arguments):
    inventory['efs'] = storage.get_efs_inventory(ownerId)

#
# ----------------- Glacier inventory
#
if ('glacier' in arguments):
    inventory['glacier'] = storage.get_glacier_inventory(ownerId)

#
# ----------------- Storage gateway inventory
#
if ('storagegateway' in arguments):
    inventory['storagegateway'] = storage.get_storagegateway_inventory(ownerId)


#################################################################
#                          DATABASES                            #
#################################################################
#
# ----------------- RDS inventory
#
if ('rds' in arguments):
    inventory['rds'] = db.get_rds_inventory(ownerId)

#
# ----------------- dynamodb inventory
#
if ('dynamodb' in arguments):
    inventory['dynamodb'] = db.get_dynamodb_inventory(ownerId)

#
# ----------------- Neptune inventory
#
if ('neptune' in arguments):
    inventory['neptune'] = db.get_neptune_inventory(ownerId)

#
# ----------------- Redshift inventory
#
if ('redshift' in arguments):
    inventory['redshift'] = db.get_redshift_inventory(ownerId)
    
#
# ----------------- Neptune inventory
#
if ('elasticache' in arguments):
    inventory['elasticache'] = db.get_elasticache_inventory(ownerId)


#################################################################
#                      SECURITY & IAM                           #
#################################################################
#
# ----------------- KMS inventory
#
if ('kms' in arguments):
    inventory['kms'] = iam.get_kms_inventory(ownerId)

#
# ----------------- Cloud directory
#
if ('clouddirectory' in arguments):
    inventory['clouddirectory'] = security.get_clouddirectory_inventory(ownerId)

#
# ----------------- ACM (Certificates) inventory
#
if ('acm' in arguments):
    inventory['acm'] = security.get_acm_inventory(ownerId)

#
# ----------------- ACMPCA (Certificates) inventory Private Certificate Authority
#
if ('acm-pca' in arguments):
    inventory['acm-pca'] = security.get_acm_inventory(ownerId)

#
# ----------------- Secrets Manager
#
if ('secrets' in arguments):
    inventory['secrets-manager'] = security.get_secrets_inventory(ownerId)
    
#
# ----------------- Cloud HSM
#
if ('hsm' in arguments):
    inventory['cloud-hsm'] = security.get_hsm_inventory(ownerId)


#################################################################
#                      DEVELOPER TOOLS                          #
#################################################################
#
# ----------------- CodeStar inventory
#
if ('codestar' in arguments):
    inventory['codestar'] = dev.get_codestar_inventory(ownerId)


#################################################################
#                         MANAGEMENT                            #
#################################################################
#
# ----------------- CloudFormation
#
if ('cloudformation' in arguments):
    inventory['cloudformation'] = mgn.get_cloudformation_inventory(ownerId)#

# ----------------- CloudTrail
#
if ('cloudtrail' in arguments):
    inventory['cloudtrail'] = mgn.get_cloudtrail_inventory(ownerId)

# ----------------- CloudWatch
#
if ('cloudwatch' in arguments):
    inventory['cloudwatch'] = mgn.get_cloudwatch_inventory(ownerId)


#################################################################
#                          NETWORK                              #
#################################################################
#
# ----------------- API Gateway inventory
#
if ('apigateway' in arguments):
    inventory['apigateway'] = net.get_apigateway_inventory(ownerId)

#
# ----------------- Route 53 inventory
#
if ('route53' in arguments):
    inventory['route53'] = net.get_route53_inventory(ownerId)

#
# ----------------- CloudFront inventory
#
if ('cloudfront' in arguments):
    inventory['cloudfront'] = net.get_cloudfront_inventory(ownerId)


#################################################################
#                   BUSINESS PRODUCTIVITY                       #
#################################################################
#
# ----------------- Alexa for Business
#
if ('alexa' in arguments):
    inventory['alexa'] = bus.get_alexa_inventory(ownerId)

#
# ----------------- WorkDocs (not implemented)
#
if ('workdocs' in arguments):
    inventory['workdocs'] = bus.get_workdocs_inventory(ownerId)

#
# ----------------- Workmail (not well tested, some rights issues)
#
if ('workmail' in arguments):
    inventory['workmail'] = bus.get_workmail_inventory(ownerId)

#
# ----------------- Cost Explorer (experimental)
#
if ('ce' in arguments):
    ce_inventory = []
    utils.display(ownerId, 'global', "cost explorer inventory", "")
    list_ce = fact.get_ce_inventory(ownerId, None).get('ResultsByTime')
    for item in list_ce:
        ce_inventory.append(json.loads(utils.json_datetime_converter(item)))
    inventory['cost-explorer'] = ce_inventory


#################################################################
#               International Resources (no region)             #
#################################################################

region_name = 'global'

#
# ----------------- S3 quick inventory
#
if ('s3' in arguments):
    inventory["s3"] = storage.get_s3_inventory(ownerId)

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

#
# This is the end
#
print()
print("End of processing.")
print()
