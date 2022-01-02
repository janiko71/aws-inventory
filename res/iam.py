import boto3
import botocore
import json
import config
import pprint, operator
import res.utils as utils
import res.glob as glob

def get_iam_inventory(oId, profile,boto3_config,selected_regions):

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "iam", 
        aws_region = "global", 
        function_name = "list_users",
        key_get = "Users",
        pagination = True
    )

def get_group_inventory(oId, profile,boto3_config,selected_regions):
  
    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "iam",
        aws_region = "global",
        function_name = "list_groups",
        key_get = "Groups",
        pagination = True   
    )

#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')
