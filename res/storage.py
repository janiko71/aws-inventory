import boto3
import botocore
from botocore.exceptions import ClientError
import pprint
import config
import json
import res.utils as utils
import res.glob as glob


"""
    Supported services   : S3 (detail), EFS (Elastic File System), Glacier, Storage Gateway, FSx
    Unsupported services : AWS Backup
"""

def get_s3_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns S3 quick inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: S3 inventory
        :rtype: json

        ..note:: #http://boto3.readthedocs.io/en/latest/reference/services/s3.html#client
    """
       
    inventory = []

    bucket_list = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "s3", 
        aws_region = "global", 
        function_name = "list_buckets", 
        key_get = "Buckets"
    )

    # S3 needs some analysis (website, size)

    session = boto3.Session(profile_name=profile)
    s3 = session.client("s3")
    
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

def get_efs_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns EFS inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: EFS inventory
        :rtype: json

        ..note:: #http://boto3.readthedocs.io/en/latest/reference/services/efs.html
    """

    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "efs", 
        aws_region = "all", 
        function_name = "describe_file_systems", 
        key_get = "FileSystems",
        pagination = True
    )

def get_glacier_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns Glacier inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: Glacier inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/glacier.html

    """
    
    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "glacier", 
        aws_region = "all", 
        function_name = "list_vaults", 
        key_get = "VaultList",
        pagination = True
    )


def get_storagegateway_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns Storage gateway inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: Storage gateway inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/storagegateway.html

    """
    
    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
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

def get_fsx_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns FSx (File Storage) inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: FSx (File Storage) inventory
        :rtype: json

        ..note:: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/fsx.html

    """

    fsx_inventory = {}
    
    fsx_inventory['fsx-backups'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "fsx", 
        aws_region = "all", 
        function_name = "describe_backups", 
        key_get = "Backups",
        pagination = True
    )
    
    fsx_inventory['fsx-data-repository-tasks'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "fsx", 
        aws_region = "all", 
        function_name = "describe_data_repository_tasks", 
        key_get = "DataRepositoryTasks",
        pagination = False
    )
    
    fsx_inventory['fsx-file-systems'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "fsx", 
        aws_region = "all", 
        function_name = "describe_file_systems", 
        key_get = "FileSystems",
        pagination = True
    )
    
    fsx_inventory['fsx-storage-virtual-machines'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "fsx", 
        aws_region = "all", 
        function_name = "describe_storage_virtual_machines", 
        key_get = "StorageVirtualMachines",
        pagination = False
    )
    
    fsx_inventory['fsx-volumes'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "fsx", 
        aws_region = "all", 
        function_name = "describe_volumes", 
        key_get = "Volumes",
        pagination = False
    )

    return fsx_inventory

#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')
