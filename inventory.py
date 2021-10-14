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
import res.glob         as glob

import res.compute      as compute
import res.container    as container
import res.storage      as storage
import res.db           as db
import res.dev          as dev
import res.iam          as iam
import res.network      as net
import res.fact         as fact
import res.security     as security
import res.analytics    as analytics
import res.management   as mgn
import res.business     as bus
import res.integration  as integ
import res.awsthread    as awsthread




# --- Argumentation. See function check_arguments.
#
# If we find log level parameter, we adjust log level.
# If we find no service name, we inventory all services.
# Else we only inventory services passed in cmd line.
# We need the region list for the 'regions' argument.

profile_name, arguments, boto3_config, selected_regions = utils.check_arguments(sys.argv[1:])
nb_arg = len(arguments)

# if no arguments, we try all AWS services
if (nb_arg == 0):
    arguments = config.SUPPORTED_COMMANDS
    arguments.remove('ce')  # For it's not free, cost explorer is removed from defaults inventory. You need to call it explicitly.

# --- Displaying execution parameters
print('-'*100)
print ('Number of services   :', len(arguments))
print ('Services List        :', str(arguments))
print('-'*100)
print()


# --- AWS basic information

ownerId = utils.get_ownerID(profile_name)
config.logger.info('OWNER ID: ' + ownerId)
config.logger.info('AWS Profile: ' + str(profile_name))


# --- Inventory initialization

inventory = {}


# --- Progression counter initialization

config.nb_units_done = 0
for svc in arguments:
    config.nb_units_todo += (config.nb_regions * config.SUPPORTED_INVENTORIES[svc])


#
# Let's rock'n roll
#

thread_list = []

# Execution time, for information
t0 = time.time()


#################################################################
#                           COMPUTE                             #
#################################################################
#
# ----------------- EC2
#

if ('ec2' in arguments):
    thread_list.append(awsthread.AWSThread("ec2", compute.get_ec2_inventory, ownerId, profile_name, boto3_config, selected_regions))
    thread_list.append(awsthread.AWSThread("ec2-network-interfaces", compute.get_interfaces_inventory, ownerId, profile_name, boto3_config, selected_regions))
    thread_list.append(awsthread.AWSThread("ec2-vpcs", compute.get_vpc_inventory, ownerId, profile_name, boto3_config, selected_regions))
    thread_list.append(awsthread.AWSThread("ec2-ebs", compute.get_ebs_inventory, ownerId, profile_name, boto3_config, selected_regions))
    thread_list.append(awsthread.AWSThread("ec2-security-groups", compute.get_sg_inventory, ownerId, profile_name, boto3_config, selected_regions))
    thread_list.append(awsthread.AWSThread("ec2-internet-gateways", compute.get_igw_inventory, ownerId, profile_name, boto3_config, selected_regions))
    thread_list.append(awsthread.AWSThread("ec2-nat-gateways", compute.get_ngw_inventory, ownerId, profile_name, boto3_config, selected_regions))
    thread_list.append(awsthread.AWSThread("ec2-subnets", compute.get_subnet_inventory, ownerId, profile_name, boto3_config, selected_regions))
    thread_list.append(awsthread.AWSThread("ec2-eips", compute.get_eips_inventory, ownerId, profile_name, boto3_config, selected_regions))
    thread_list.append(awsthread.AWSThread("ec2-egpus", compute.get_egpus_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Lambda functions
#
if ('lambda' in arguments):
    thread_list.append(awsthread.AWSThread("lambda", compute.get_lambda_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Elastic beanstalk
#
if ('elasticbeanstalk' in arguments):
    thread_list.append(awsthread.AWSThread("elasticbeanstalk-environments", compute.get_elasticbeanstalk_environments_inventory, ownerId, profile_name, boto3_config, selected_regions))
    thread_list.append(awsthread.AWSThread("elasticbeanstalk-applications", compute.get_elasticbeanstalk_applications_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Lighstail instances
#
if ('lightsail' in arguments):
    thread_list.append(awsthread.AWSThread('lightsail', compute.get_lightsail_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Autoscaling
#
if ('autoscaling' in arguments):
    thread_list.append(awsthread.AWSThread('autoscaling', compute.get_autoscaling_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Serverless repository
#
if ('serverlessrepo' in arguments):
    thread_list.append(awsthread.AWSThread('serverlessrepo',compute.get_serverlessrepo_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- AWS Outposts
#
if ('outposts' in arguments):
    thread_list.append(awsthread.AWSThread('outposts',compute.get_outposts_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Batch jobs inventory
#
if ('batch' in arguments):
    thread_list.append(awsthread.AWSThread('batch', compute.get_batch_inventory, ownerId, profile_name, boto3_config, selected_regions))


#################################################################
#                          CONTAINER                            #
#################################################################
#
# ----------------- EKS inventory
#
if ('eks' in arguments):
    thread_list.append(awsthread.AWSThread('eks',container.get_eks_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- ECS
#
if ('ecs' in arguments):
    thread_list.append(awsthread.AWSThread("ecs-clusters", container.get_ecs_inventory, ownerId, profile_name, boto3_config, selected_regions))
    thread_list.append(awsthread.AWSThread("ecs-tasks", container.get_ecs_tasks_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- ECR
#
if ('ecr' in arguments):
    thread_list.append(awsthread.AWSThread("ecr", container.get_ecr_inventory, ownerId, profile_name, boto3_config, selected_regions))


#################################################################
#                           STORAGE                             #
#################################################################
#
# ----------------- EFS inventory
#
if ('efs' in arguments):
    thread_list.append(awsthread.AWSThread('efs', storage.get_efs_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Glacier inventory
#
if ('glacier' in arguments):
    thread_list.append(awsthread.AWSThread('glacier', storage.get_glacier_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Storage gateway inventory
#
if ('storagegateway' in arguments):
    thread_list.append(awsthread.AWSThread('storagegateway', storage.get_storagegateway_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- FSx inventory
#
if ('fsx' in arguments):
    thread_list.append(awsthread.AWSThread('fsx', storage.get_fsx_inventory, ownerId, profile_name, boto3_config, selected_regions))


#################################################################
#                          DATABASES                            #
#################################################################
#
# ----------------- RDS inventory
#
if ('rds' in arguments):
    thread_list.append(awsthread.AWSThread('rds', db.get_rds_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- dynamodb inventory
#
if ('dynamodb' in arguments):
    thread_list.append(awsthread.AWSThread('dynamodb', db.get_dynamodb_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Neptune inventory
#
if ('neptune' in arguments):
    thread_list.append(awsthread.AWSThread('neptune', db.get_neptune_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Redshift inventory
#
if ('redshift' in arguments):
    thread_list.append(awsthread.AWSThread('redshift', db.get_redshift_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Elasticache inventory
#
if ('elasticache' in arguments):
    thread_list.append(awsthread.AWSThread('elasticache', db.get_elasticache_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- QLDB inventory
#
if ('qldb' in arguments):
    thread_list.append(awsthread.AWSThread('qldb', db.get_qldb_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- DocDB inventory
#
if ('docdb' in arguments):
    thread_list.append(awsthread.AWSThread('docdb', db.get_docdb_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- MemoryDB inventory
#
if ('memorydb' in arguments):
    thread_list.append(awsthread.AWSThread('memorydb', db.get_memorydb_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Timestream inventory
#
if ('timestream' in arguments):
    thread_list.append(awsthread.AWSThread('timestream', db.get_timestream_inventory, ownerId, profile_name, boto3_config, selected_regions))


#################################################################
#                      SECURITY & IAM                           #
#################################################################
#
# ----------------- KMS inventory
#
if ('kms' in arguments):
    thread_list.append(awsthread.AWSThread('kms', iam.get_kms_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Cloud directory
#
if ('clouddirectory' in arguments):
    thread_list.append(awsthread.AWSThread('clouddirectory', security.get_clouddirectory_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- ACM (Certificates) inventory
#
if ('acm' in arguments):
    thread_list.append(awsthread.AWSThread('acm', security.get_acm_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- ACMPCA (Certificates) inventory Private Certificate Authority
#
if ('acm-pca' in arguments):
    thread_list.append(awsthread.AWSThread('acm-pca', security.get_acm_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Secrets Manager
#
if ('secrets' in arguments):
    thread_list.append(awsthread.AWSThread('secrets', security.get_secrets_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Cloud HSM
#
if ('hsm' in arguments):
    thread_list.append(awsthread.AWSThread('hsm', security.get_hsm_inventory, ownerId, profile_name, boto3_config, selected_regions))


#################################################################
#                      DEVELOPER TOOLS                          #
#################################################################
#
# ----------------- CodeStar inventory
#
if ('codestar' in arguments):
    thread_list.append(awsthread.AWSThread('codestar', dev.get_codestar_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- CodeCommit inventory
#
if ('codecommit' in arguments):
    thread_list.append(awsthread.AWSThread('codecommit', dev.get_codecommit_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- CodeArtifact inventory
#
if ('codeartifact' in arguments):
    thread_list.append(awsthread.AWSThread('codeartifact', dev.get_codeartifact_inventory, ownerId, profile_name, boto3_config, selected_regions))


#################################################################
#                        INTEGRATION                            #
#################################################################
#
# ----------------- Simple Queue Service inventory
#
if ('sqs' in arguments):
    thread_list.append(awsthread.AWSThread('sqs', integ.get_sqs_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Amazon MQ inventory
#
if ('mq' in arguments):
    thread_list.append(awsthread.AWSThread('mq', integ.get_mq_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Simple Notification Serv ice inventory
#
if ('sns' in arguments):
    thread_list.append(awsthread.AWSThread('sns', integ.get_sns_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Step Functions inventory
#
if ('stepfunctions' in arguments):
    thread_list.append(awsthread.AWSThread('stepfunctions', integ.get_stepfunctions_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Appflow inventory
#
if ('appflow' in arguments):
    thread_list.append(awsthread.AWSThread('appflow', integ.get_appflow_inventory, ownerId, profile_name, boto3_config, selected_regions))


#################################################################
#                         ANALYTICS                             #
#################################################################
#
# ----------------- ElasticSearch
#
if ('es' in arguments):
    thread_list.append(awsthread.AWSThread('es', analytics.get_es_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Cloudsearch
#
if ('cloudsearch' in arguments):
    thread_list.append(awsthread.AWSThread('cloudsearch', analytics.get_cloudsearch_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Data Pipeline
#
if ('datapipeline' in arguments):
    thread_list.append(awsthread.AWSThread('datapipeline', analytics.get_datapipeline_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Elastic MapReduce
#
if ('emr' in arguments):
    thread_list.append(awsthread.AWSThread('emr', analytics.get_emr_inventory, ownerId, profile_name, boto3_config, selected_regions))


#################################################################
#                         MANAGEMENT                            #
#################################################################
#
# ----------------- CloudFormation
#
if ('cloudformation' in arguments):
    thread_list.append(awsthread.AWSThread('cloudformation', mgn.get_cloudformation_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- CloudTrail
#
if ('cloudtrail' in arguments):
    thread_list.append(awsthread.AWSThread('cloudtrail', mgn.get_cloudtrail_inventory, ownerId, profile_name, boto3_config, selected_regions))

# ----------------- CloudWatch
#
if ('cloudwatch' in arguments):
    thread_list.append(awsthread.AWSThread('cloudwatch', mgn.get_cloudwatch_inventory, ownerId, profile_name, boto3_config, selected_regions))


#################################################################
#                          NETWORK                              #
#################################################################
#
# ----------------- API Gateway inventory
#
if ('apigateway' in arguments):
    thread_list.append(awsthread.AWSThread('apigateway', net.get_apigateway_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Route 53 inventory
#
if ('route53' in arguments):
    thread_list.append(awsthread.AWSThread('route53', net.get_route53_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- CloudFront inventory
#
if ('cloudfront' in arguments):
    thread_list.append(awsthread.AWSThread('cloudfront', net.get_cloudfront_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Load Balancer inventory
#
if ('elb' in arguments):
    thread_list.append(awsthread.AWSThread('elb', net.get_elb_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Load Balancer v2 inventory
#
if ('elbv2' in arguments):
    thread_list.append(awsthread.AWSThread('elbv2', net.get_elbv2_inventory, ownerId, profile_name, boto3_config, selected_regions))


#################################################################
#                   BUSINESS PRODUCTIVITY                       #
#################################################################
#
# ----------------- Alexa for Business
#
if ('alexa' in arguments):
    thread_list.append(awsthread.AWSThread('alexa', bus.get_alexa_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- WorkDocs (not implemented)
#
if ('workdocs' in arguments):
    thread_list.append(awsthread.AWSThread('workdocs', bus.get_workdocs_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Workmail (not well tested, some rights issues)
#
if ('workmail' in arguments):
    thread_list.append(awsthread.AWSThread('workmail', bus.get_workmail_inventory, ownerId, profile_name, boto3_config, selected_regions))

#
# ----------------- Cost Explorer (experimental)
#
if ('ce' in arguments):
    ce_inventory = []
    """utils.display(ownerId, 'global', "cost explorer inventory", "")
    list_ce = fact.get_ce_inventory(ownerId, None).get('ResultsByTime')
    for item in list_ce:
        ce_inventory.append(json.loads(utils.json_datetime_converter(item)))
    inventory['cost-explorer'] = ce_inventory"""


#################################################################
#               International Resources (no region)             #
#################################################################

region_name = 'global'

#
# ----------------- S3 quick inventory
#
if ('s3' in arguments):
    thread_list.append(awsthread.AWSThread('s3', storage.get_s3_inventory, ownerId, profile_name, boto3_config, selected_regions))



# -------------------------------------------------------------------
#
#                         Thread management
#
# -------------------------------------------------------------------

for th in thread_list:
    th.start()

for th in thread_list:
    th.join()

#
# ----------------- Gathering all inventories
#
for svc in arguments:

    # Some particular cases
    if (svc == "ec2"):

        inventory["ec2"] = config.global_inventory["ec2"]
        inventory["ec2-network-interfaces"] = config.global_inventory["ec2-network-interfaces"]
        inventory["ec2-ebs"] = config.global_inventory["ec2-ebs"]
        inventory["ec2-vpcs"] = config.global_inventory["ec2-vpcs"]
        inventory["ec2-security-groups"] = config.global_inventory["ec2-security-groups"]
        inventory["ec2-internet-gateways"] = config.global_inventory["ec2-internet-gateways"]
        inventory["ec2-nat-gateways"] = config.global_inventory["ec2-nat-gateways"]
        inventory["ec2-subnets"] = config.global_inventory["ec2-subnets"]
        inventory["ec2-eips"] = config.global_inventory["ec2-eips"]
        inventory["ec2-egpu"] = config.global_inventory["ec2-egpus"]

    elif (svc == "ecs"):

        inventory["ecs"] = {
            "ecs-clusters": config.global_inventory["ecs-clusters"],
            "ecs-tasks": config.global_inventory["ecs-tasks"]
        }

    elif (svc == "elasticbeanstalk"):

        inventory["elasticbeanstalk"] = {
            "elasticbeanstalk-environments": config.global_inventory["elasticbeanstalk-environments"],
            "elasticbeanstalk-applications": config.global_inventory["elasticbeanstalk-applications"]
        }

    else:

        # General case
        inventory[svc] = config.global_inventory[svc]


execution_time = time.time() - t0
print("\n\nAll inventories are done. Duration: {:2f} seconds\n".format(execution_time))

#
# ----------------- Final inventory
#

filename_json = 'AWS_{}_{}.json'.format(ownerId, config.timestamp)
try:
    json_file = open(config.filepath+filename_json,'w+')
except IOError as e:
    config.logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))

json_file.write(json.JSONEncoder().encode(inventory))
json_file.close()

#
# ----------------- For Information: list of regions and availability zones
#

filename_regions_json = 'AWS_Regions_List.json'
try:
    json_file = open(config.filepath+filename_regions_json,'w+')
except IOError as e:
    config.logger.error("I/O error({0}): {1}".format(e.errno, e.strerror))

json_file.write(json.JSONEncoder().encode(config.regions))
json_file.close()

#
# EOF
#

#
# This is the end
#
print("End of processing.\n")
