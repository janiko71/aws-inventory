import time
import logging
import json
import os
import boto3, botocore
from time import gmtime, strftime


#
# Environment Variables & File handling & logging
#

# --- Format for displaying actions

display = "OwnerID : {} ! {:6.2f} % ! Region : {:16} ! {} ({}){}"


# --- Initial values for inventory files names

t = gmtime()
timestamp = strftime("%Y%m%d%H%M%S", t)
filepath = "./output/"
os.makedirs(filepath, exist_ok=True)


# --- logging variables

log_filepath    = "./log/"
os.makedirs(log_filepath, exist_ok=True)

logger          = logging.getLogger("aws-inventory")
hdlr            = logging.FileHandler(log_filepath+"inventory.log")
formatter       = logging.Formatter("%(asctime)s %(levelname)s %(message)s")


# --- Log handler

hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)


# --- If needed: S3 bucket name to write inventory

S3_INVENTORY_BUCKET="s3-bucket"


# --- Arguments/Supported commands

SUPPORTED_INVENTORIES = {"s3": 1, "ec2": 11, "lambda": 1, "lightsail": 4, "efs": 1, "glacier": 1, "rds": 2, "ce": 1, "kms": 1, "dynamodb": 1, "apigateway": 1,
    "ecs": 2, "elasticbeanstalk": 2, "clouddirectory": 1, "codestar": 1, "alexa": 1, "workmail": 1, "neptune": 1, "acm": 1, "acm-pca": 1, "autoscaling": 3,
    "cloudformation": 1, "cloudtrail": 1, "cloudwatch": 1, "eks": 1, "batch": 3, "route53": 3, "cloudfront": 1, "secrets": 1, "hsm": 1, "elasticache": 2,
	"redshift": 2, "storagegateway": 1, "sqs": 1, "mq": 2, "sns": 2, "es": 1, "cloudsearch": 1, "datapipeline": 1, "elb": 1, "elbv2": 1, "emr": 3,
    "serverlessrepo": 1, "outposts": 2, "ecr": 2, "qldb": 1, "docdb": 2, "memorydb": 1, "timestream": 1, "stepfunctions": 2,
    "codecommit": 1, "codeartifact": 2, "fsx": 5, "appflow": 1, "events": 6, "waf": 4, "guardduty": 1, "sagemaker": 3, "forecast": 2,
    "kinesis": 1, "athena": 1, "managedblockchain": 1, "qldb": 1 }
SUPPORTED_COMMANDS = list(SUPPORTED_INVENTORIES.keys())
SUPPORTED_PARAMETERS = ["debug", "info", "warning", "error"]


# --- Counters

nb_svc = 0
nb_units_todo = 0
nb_units_done = 0
regions = []
nb_regions = 0

#
# --- Global inventory, for multithreading purpose
#
global_inventory = {}
