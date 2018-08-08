# Python imports
import boto3
from botocore.exceptions import ClientError
import botocore
import collections
import datetime
import time
import dateutil
from dateutil.tz import tzutc
import csv
import json
from time import gmtime, strftime
import smtplib
import os, hmac, hashlib
import pprint
import logging
from sys import exit

# AWS Services imports 
import res.ec2 as ec2
import res.s3 as s3

#
#  Useful functions
#
def write_json(file, info):
    file.write(info)
    return

def datetime_converter(dt):
    if isinstance(dt, datetime.datetime):
        return dt.__str__()  

def json_datetime_converter(json_text):
    return json.dumps(json_text, default = datetime_converter)      

def get_ownerID():
    """
        Get owner ID of the AWS account we are working on

        :return: owner ID
        :rtype: string
    """   
    sts = boto3.client('sts')
    identity = sts.get_caller_identity()
    ownerId = identity['Account']
    return ownerId

#
# Environment Variables & File handling & logging
#

# --- AWS basic information
ownerId = get_ownerID()

# --- AWS Regions 
with open('aws_regions.json') as json_file:
    aws_regions = json.load(json_file)
regions = aws_regions.get('Regions',[] ) 

# --- Initial values for inventory files names
t = gmtime()
timestamp = strftime("%Y%m%d%H%M%S", t)
filepath = './output/'
filename_json = 'AWS_{}_{}.json'.format(ownerId, timestamp)
# --- logging variables
log_filepath = './log/'
logger       = logging.getLogger('aws-inventory')
hdlr         = logging.FileHandler(log_filepath+'inventory.log')
formatter    = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
# --- Log handler
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)
# --- csv_file = open(filepath+filename,'w+')logging.basicConfig(filename='example.log',level=logging.DEBUG)
S3_INVENTORY_BUCKET="xx"


# 
# ----------------- EC2
#

# Lookup in every AWS Region

# Initialization for some variables
inventory = {}
ec2_inventory = []
interfaces_inventory = interfaces_analysis = []

for current_region in regions:
   
    current_region_name = current_region['RegionName']
    print('OwnerID : {}, EC2 inventory, Region : {}'.format(ownerId, current_region_name))

    # EC2
    instances = ec2.get_ec2_inventory(current_region_name)
    for instance in instances:
        json_ec2_desc = json.loads(json_datetime_converter(instance))
        ec2_inventory.append(ec2.get_ec2_analysis(json_ec2_desc, current_region_name))

    # Network
    for ifc in ec2.get_interfaces_inventory(current_region_name):
        interfaces_inventory.append(json.loads(json_datetime_converter(ifc)))

    # VPCs

    # EBS

inventory["ec2"] = ec2_inventory
inventory["ec2-interfaces"] = interfaces_inventory

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
    logging.error("I/O error({0}): {1}".format(e.errno, e.strerror))

json_file.write(json.JSONEncoder().encode(inventory))

#
# EOF
#
json_file.close()

