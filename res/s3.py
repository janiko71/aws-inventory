import boto3
import botocore
from botocore.exceptions import ClientError
import pprint
import config

def get_s3_inventory(region_name):
    """
        Returns S3 quick inventory

        :param region: region name
        :type region: string

        :return: S3 inventory
        :rtype: json

        ..note:: #http://boto3.readthedocs.io/en/latest/reference/services/s3.html#client
    """
    config.logger.info('s3 inventory, region {}, get_s3_inventory'.format(region_name))
    
    inventory = []
    s3 = boto3.client('s3')
    
    listbuckets = s3.list_buckets().get('Buckets')
    
    if len(listbuckets) > 0:
        for bucket in listbuckets:
            #http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.list_objects_v2
            bucketname = bucket['Name']
            this_bucket = {bucketname: []}
            # Check if a website if configured; if yes, it could lead to a DLP issue
            has_website = 'unknown'
            try:
                s3.get_bucket_website(Bucket = bucketname)
                has_website = 'yes'
            except ClientError as ce:
                if 'NoSuchWebsiteConfiguration' in ce.args[0]:
                    has_website = 'no'
            # Summarize nb of objets and total size (for the current bucket)
            this_bucket['has_website'] = has_website
            paginator = s3.get_paginator('list_objects_v2')
            nbobj = 0
            size = 0
            #page_objects = paginator.paginate(Bucket=bucketname,PaginationConfig={'MaxItems': 10})
            page_objects = paginator.paginate(Bucket = bucketname)
            for objects in page_objects:
                nbobj += len(objects['Contents'])
                for obj in objects['Contents']:
                    size += obj['Size']
            this_bucket['number_of_objects'] = nbobj
            this_bucket['total_size'] = size
            inventory.append(this_bucket)
    
    return inventory


# Hey, doc: we're in a module!
if (__name__ == '__main__'):
    print('Module => Do not execute')