import boto3
import botocore
from botocore.exceptions import ClientError
import pprint
import config
import json
import res.utils as utils
import res.glob as glob

# =======================================================================================================================
#
#  Supported services   : S3 (detail), EFS (Elastic File System), Glacier, Storage Gateway
#  Unsupported services : None
#
# =======================================================================================================================

#  ------------------------------------------------------------------------
#
#    S3
#
#  ------------------------------------------------------------------------

def get_s3_inventory(oId):

    """
        Returns S3 quick inventory

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: S3 inventory
        :rtype: json

        ..note:: #http://boto3.readthedocs.io/en/latest/reference/services/s3.html#client
    """
       
    inventory = []

    bucket_list = glob.get_inventory(
        ownerId = oId,
        aws_service = "s3", 
        aws_region = "global", 
        function_name = "list_buckets", 
        key_get = "Buckets"
    )

    # S3 needs some analysis (website, size)

    s3 = boto3.client("s3")
    
    if len(bucket_list) > 0:

        for bucket in bucket_list:

            bucket_name = bucket['Name']

            # Check if a website if configured; if yes, it could lead to a DLP issue
            try:
                has_website = 'unknown'
                has_website = s3.get_bucket_website(Bucket = bucket_name)
                del has_website['ResponseMetadata']
            except ClientError as ce:
                if 'NoSuchWebsiteConfiguration' in ce.args[0]:
                    has_website = 'no'
            bucket['website'] = has_website

            # Tags
            try:
                bucket['tags'] = s3.get_bucket_tagging(Bucket = bucket_name).get('TagSet')
            except:
                pass

            # ACL
            try:
                acl = s3.get_bucket_acl(Bucket = bucket_name)
                del acl['ResponseMetadata']
                bucket['acl'] = acl              
            except:
                pass
            
            # Policy
            try:
                policy = "no"
                policy = json.JSONDecoder().decode(s3.get_bucket_policy(Bucket = bucket_name).get('Policy'))
                del policy['ResponseMetadata']
            except:
                pass
            bucket['policy'] = policy

            # Encryption
            try:
                encrypt = "no"
                encrypt = s3.get_bucket_encryption(Bucket = bucket_name)
                del encrypt['ResponseMetadata']
            except:
                pass
            bucket['encryption'] = encrypt  

            # Other
            bucket['location'] = s3.get_bucket_location(Bucket = bucket_name).get('LocationConstraint')

            # Summarize nb of objets and total size (for the current bucket)
            paginator = s3.get_paginator('list_objects_v2')
            nbobj = 0
            size = 0
            #page_objects = paginator.paginate(Bucket=bucketname,PaginationConfig={'MaxItems': 10})
            page_objects = paginator.paginate(Bucket = bucket_name)
            for objects in page_objects:
                try:
                    nbobj += len(objects['Contents'])
                    for obj in objects['Contents']:
                        size += obj['Size']
                except:
                    pass
            bucket['number_of_objects'] = nbobj
            bucket['total_size'] = size

            inventory.append(bucket)

    return inventory


#  ------------------------------------------------------------------------
#
#    EFS (Elastic File System)
#
#  ------------------------------------------------------------------------

def get_efs_inventory(oId):

    """
        Returns EFS inventory

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: EFS inventory
        :rtype: json

        ..note:: #http://boto3.readthedocs.io/en/latest/reference/services/efs.html
    """

    return glob.get_inventory(
        ownerId = oId,
        aws_service = "efs", 
        aws_region = "all", 
        function_name = "describe_file_systems", 
        key_get = "FileSystems",
        pagination = True
    )


#  ------------------------------------------------------------------------
#
#    Glacier
#
#  ------------------------------------------------------------------------

def get_glacier_inventory(oId):

    """
        Returns Glacier inventory

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: Glacier inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/glacier.html

    """
    
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "glacier", 
        aws_region = "all", 
        function_name = "list_vaults", 
        key_get = "VaultList",
        pagination = True
    )


#  ------------------------------------------------------------------------
#
#    Storage Gateway
#
#  ------------------------------------------------------------------------

def get_storagegateway_inventory(oId):

    """
        Returns Storage gateway inventory

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: Storage gateway inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/storagegateway.html

    """
    
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "storagegateway", 
        aws_region = "all", 
        function_name = "list_gateways", 
        key_get = "Gateways",
        detail_function = "describe_gateway_information",
        detail_get_key = "",
        join_key = "GatewayARN",
        detail_join_key = "GatewayARN",
        pagination = True
    )


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')