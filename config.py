import time
import logging
import json
import os
from time import gmtime, strftime

#
# Environment Variables & File handling & logging
#

# --- Format for displaying actions

display = "OwnerID : {} ! {:6.2f} % ! Region : {:16} ! {} ({}){}"


# --- Initial values for inventory files names

t = gmtime()
timestamp = strftime("%Y%m%d%H%M%S", t)
filepath = './output/'
os.makedirs(filepath, exist_ok=True)


# --- logging variables

log_filepath    = './log/'
os.makedirs(log_filepath, exist_ok=True)

logger          = logging.getLogger('aws-inventory')
hdlr            = logging.FileHandler(log_filepath+'inventory.log')
formatter       = logging.Formatter('%(asctime)s %(levelname)s %(message)s')


# --- Log handler

hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)


# --- If needed: S3 bucket name to write inventory

S3_INVENTORY_BUCKET="s3-bucket"


# --- Arguments/Supported commands

SUPPORTED_INVENTORIES = {'s3': 1, 'ec2': 4, 'lambda': 1 , 'lightsail': 3, 'efs': 1, 'glacier': 1, 'rds': 1, 'ce': 1, 'kms': 1, 'dynamodb': 1, 'apigateway': 1,
    'ecs': 2, 'elasticbeanstalk': 2, 'clouddirectory': 1, 'codestar': 1, 'alexa': 1, 'workmail': 1, 'neptune': 1, 'acm': 1, 'acm-pca': 1, 'autoscaling': 3,
    'cloudformation': 1, 'cloudtrail': 1, 'cloudwatch': 1, 'eks': 1, 'batch': 3, 'route53': 3, 'cloudfront': 1, 'secrets': 1, 'hsm': 3, 'elasticache': 2,
	'redshift': 2, 'storagegateway': 1, 'sqs': 1}
SUPPORTED_COMMANDS = list(SUPPORTED_INVENTORIES.keys())
SUPPORTED_PARAMETERS = ['debug', 'info', 'warning', 'error']


# --- AWS Regions 

with open('aws_regions.json') as json_file:
    aws_regions = json.load(json_file)
regions = aws_regions.get('Regions',[]) 


# --- Counters

nb_svc = 0
nb_regions = len(regions)
nb_units_todo = 0
nb_units_done = 0

#
# --- Global inventory, for multithreading purpose
#
global_inventory = {}
