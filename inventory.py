# Python imports
import boto3
import botocore
import collections
import datetime
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

# AWS Regions 
with open('aws_regions.json') as json_file:
    aws_regions = json.load(json_file)

# Environment Variables & File handling
S3_INVENTORY_BUCKET="xx"

# Initial values for inventory files
date_fmt = strftime("%Y_%m_%d", gmtime())
filepath ='./'
filename_csv ='AWS_Resources_' + date_fmt + '.csv'
filename_json ='AWS_Resources_' + date_fmt + '.json'
#csv_file = open(filepath+filename,'w+')

def write_inventory(file,res,owner,region,resid,restype,state,tags,addcat,details):
    file.write("%s,%s,%s,%s,%s,%s,%s,%s,%s\n"%(res,owner,region,resid,restype,state,tags,addcat,details))
    csv_file.flush()
    return

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
        Get owner ID 

        :return: owner ID
        :rtype: string
    """   
    sts = boto3.client('sts')
    identity = sts.get_caller_identity()
    ownerId = identity['Account']
    return ownerId

try:
    json_file = open(filepath+filename_json,'w+')
except IOError as e:
    print ("I/O error({0}): {1}".format(e.errno, e.strerror))

ownerId = get_ownerID()
regions = aws_regions.get('Regions',[] )

#
# Lookup in every AWS Region
# 

ec2_json = {"ec2" : []}

for current_region in regions:
    
    current_region_name = current_region['RegionName']
    disp = 'OwnerID : {}, Region : {}'.format(ownerId, current_region_name)
    pprint.pprint(disp)

    # EC2
    ec2_inventory = ec2.get_ec2_inventory(current_region_name)
    for instance in ec2_inventory:
        ec2_json["ec2"].append(json.loads(json_datetime_converter(instance)))

json_file.write(json.JSONEncoder().encode(ec2_json))

#
# EOF
#
json_file.close()