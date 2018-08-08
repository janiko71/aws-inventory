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
from sys import exit

# AWS Services imports 
import res.ec2 as ec2
import res.s3 as s3

# AWS Regions 
with open('aws_regions.json') as json_file:
    aws_regions = json.load(json_file)

# Environment Variables & File handling
S3_INVENTORY_BUCKET="xx"

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

ownerId = get_ownerID()
regions = aws_regions.get('Regions',[] ) 

# 
# ----------------- EC2
#

inventory = {"ec2" : []}

# Lookup in every AWS Region

for current_region in regions:
    
    current_region_name = current_region['RegionName']
    print('OwnerID : {}, EC2 inventory, Region : {}'.format(ownerId, current_region_name))

    # EC2
    ec2_inventory = ec2.get_ec2_inventory(current_region_name)
    ec2_analysis = []
    for instance in ec2_inventory:
        inventory["ec2"].append(json.loads(json_datetime_converter(instance)))
        ec2_analysis.append(ec2.get_ec2_analysis(instance))

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

# Initial values for inventory files names
t = gmtime()
timestamp = strftime("%Y%m%d%H%M%S", t)
filepath = './tests/'
filename_csv = 'AWS_{}_{}.csv'.format(ownerId, timestamp)
filename_json = 'AWS_{}_{}.json'.format(ownerId, timestamp)
#csv_file = open(filepath+filename,'w+')

try:
    json_file = open(filepath+filename_json,'w+')
except IOError as e:
    print ("I/O error({0}): {1}".format(e.errno, e.strerror))

json_file.write(json.JSONEncoder().encode(inventory))

#
# EOF
#
json_file.close()

