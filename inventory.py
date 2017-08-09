import boto3
import collections
import datetime
import csv
import json
from time import gmtime, strftime
import smtplib
#from email.MIMEMultipart import MIMEMultipart
#from email.MIMEBase import MIMEBase
#from email.MIMEText import MIMEText
#from email import Encoders
import os, hmac, hashlib
import pprint
from sys import exit
from botocore import exceptions
from botocore.exceptions import ClientError

# AWS Regions 
with open('aws_regions.json') as json_file:
    aws_regions = json.load(json_file)

# Session opening with AK/SK
session = boto3.Session(
    aws_access_key_id='xx',
    aws_secret_access_key='xx',
)

#Find current owner ID
sts = session.client('sts')
identity = sts.get_caller_identity()
ownerId = identity['Account']
pprint.pprint("OwnerID : "+ownerId)

#EC2 connection beginning
#ec = boto3.client('ec2')
#S3 connection beginning
#s3 = boto3.resource('s3')

#Environment Variables & File handling
S3_INVENTORY_BUCKET="xx"

#get to the current date
date_fmt = strftime("%Y_%m_%d", gmtime())
#Give your file path
filepath ='AWS_Resources_' + date_fmt + '.csv'
#Give your filename
filename ='AWS_Resources_' + date_fmt + '.csv'
csv_file = open(filepath,'w+')

#
# Lookup in every AWS Region
# 
regions = aws_regions.get('Regions',[] )
for region in regions:
    
        reg=region['RegionName']
        regname='REGION :' + reg
        pprint.pprint(regname)

        #
        # EC2 connection beginning
        #
        ec2con = session.client('ec2',region_name=reg)
        #boto3 library ec2 API describe instance page
        #http://boto3.readthedocs.org/en/latest/reference/services/ec2.html#EC2.Client.describe_instances
        reservations = ec2con.describe_instances().get(
        'Reservations',[]
        )
        instances = sum(
            [
                [i for i in r['Instances']]
                for r in reservations
            ], [])
        instanceslist = len(instances)
        if instanceslist > 0:
            csv_file.write("%s,%s,%s,%s,%s,%s\n"%('','','','','',''))
            csv_file.write("%s,%s\n"%('EC2 INSTANCE',regname))
            csv_file.write("%s,%s,%s,%s,%s,%s,%s\n"%('InstanceID','Instance_State','InstanceName','Instance_Type','LaunchTime','Instance_Placement', 'SecurityGroupsStr'))
            csv_file.flush()

        for instance in instances:
            state=instance['State']['Name']
            if state =='running':
                #for tags in instance['InstanceId']:
                #    Instancename= tags
                #    key= tags['Key']
                #    if key == 'Name' :
                Instancename=instance.get('Name','none')
                instanceid=instance['InstanceId']
                instancetype=instance['InstanceType']
                launchtime =instance['LaunchTime']
                Placement=instance['Placement']['AvailabilityZone']
                securityGroups = instance['SecurityGroups']
                securityGroupsStr = ''
                for idx, securityGroup in enumerate(securityGroups):
                    if idx > 0:
                        securityGroupsStr += '; '
                    securityGroupsStr += securityGroup['GroupName']
                csv_file.write("%s,%s,%s,%s,%s,%s,%s\n"% (instanceid,state,Instancename,instancetype,launchtime,Placement,securityGroupsStr))
                csv_file.flush()

        for instance in instances:
            state=instance['State']['Name']
            if state =='stopped':
                Instancename=instance.get('Name','noname')
                instanceid=instance['InstanceId']
                instancetype=instance['InstanceType']
                launchtime =instance['LaunchTime']
                Placement=instance['Placement']['AvailabilityZone']
                csv_file.write("%s,%s,%s,%s,%s,%s\n"%(instanceid,state,Instancename,instancetype,launchtime,Placement))
                csv_file.flush()

        #boto3 library ec2 API describe volumes page
        #http://boto3.readthedocs.org/en/latest/reference/services/ec2.html#EC2.Client.describe_volumes
        ec2volumes = ec2con.describe_volumes().get('Volumes',[])
        volumes = sum(
            [
                [i for i in r['Attachments']]
                for r in ec2volumes
            ], [])
        volumeslist = len(volumes)
        if volumeslist > 0:
            csv_file.write("%s,%s,%s,%s\n"%('','','',''))
            csv_file.write("%s,%s\n"%('EBS Volume',regname))
            csv_file.write("%s,%s,%s,%s\n"%('VolumeId','InstanceId','AttachTime','State'))
            csv_file.flush()

        for volume in volumes:
            VolumeId=volume['VolumeId']
            InstanceId=volume['InstanceId']
            State=volume['State']
            AttachTime=volume['AttachTime']
            csv_file.write("%s,%s,%s,%s\n" % (VolumeId,InstanceId,AttachTime,State))
            csv_file.flush()
            
        #boto3 library ec2 API describe snapshots page
        #http://boto3.readthedocs.org/en/latest/reference/services/ec2.html#EC2.Client.describe_snapshots
        ec2snapshot = ec2con.describe_snapshots(OwnerIds=[
            ownerId,
        ],).get('Snapshots',[])
        ec2snapshotlist = len(ec2snapshot)
        if ec2snapshotlist > 0:
            csv_file.write("%s,%s,%s,%s,%s\n" % ('','','','',''))
            csv_file.write("%s,%s\n"%('EC2 SNAPSHOT',regname))
            csv_file.write("%s,%s,%s,%s,%s\n" % ('SnapshotId','VolumeId','StartTime','VolumeSize','Description'))
            csv_file.flush()

        for snapshots in ec2snapshot:
            SnapshotId=snapshots['SnapshotId']
            VolumeId=snapshots['VolumeId']
            StartTime=snapshots['StartTime']
            VolumeSize=snapshots['VolumeSize']
            Description=snapshots['Description']
            csv_file.write("%s,%s,%s,%s,%s\n" % (SnapshotId,VolumeId,StartTime,VolumeSize,Description))
            csv_file.flush()

        #boto3 library ec2 API describe addresses page
        #http://boto3.readthedocs.org/en/latest/reference/services/ec2.html#EC2.Client.describe_addresses
        addresses = ec2con.describe_addresses().get('Addresses',[] )
        addresseslist = len(addresses)
        if addresseslist > 0:
            csv_file.write("%s,%s,%s,%s,%s\n"%('','','','',''))
            csv_file.write("%s,%s\n"%('EIPS INSTANCE',regname))
            csv_file.write("%s,%s,%s,%s\n"%('PublicIp','AllocationId','Domain','InstanceId'))
            csv_file.flush()

            for address in addresses:
                PublicIp=address['PublicIp']
                try:
                    AllocationId=address['AllocationId']
                except:
                    AllocationId="empty"
                Domain=address['Domain']
                instanceId=address['InstanceId']
                csv_file.write("%s,%s,%s,%s\n"%(PublicIp,AllocationId,Domain,instanceId))
                csv_file.flush()


        def printSecGroup(groupType, permission):
            ipProtocol = permission['IpProtocol']
            try:
                fromPort = permission['FromPort']
            except KeyError:
                fromPort = None
            try:
                toPort = permission['ToPort']
            except KeyError:
                toPort = None
            try:
                ipRanges = permission['IpRanges']
            except KeyError:
                ipRanges = []
            ipRangesStr = ''
            for idx, ipRange in enumerate(ipRanges):
                if idx > 0:
                    ipRangesStr += '; '
                ipRangesStr += ipRange['CidrIp']
                csv_file.write("%s,%s,%s,%s,%s,%s\n"%(groupName,groupType,ipProtocol,fromPort,toPort,ipRangesStr))
                csv_file.flush()

        #boto3 library ec2 API describe security groups page
        #http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Client.describe_security_groups
        securityGroups = ec2con.describe_security_groups().get('SecurityGroups')
        if len(securityGroups) > 0:
            csv_file.write("%s,%s,%s,%s,%s\n"%('','','','',''))
            csv_file.write("%s,%s\n"%('SEC GROUPS',regname))
            csv_file.write("%s,%s,%s,%s,%s,%s\n"%('GroupName','GroupType','IpProtocol','FromPort','ToPort','IpRangesStr'))
            csv_file.flush()
            for securityGroup in securityGroups:
                groupName = securityGroup['GroupName']
                ipPermissions = securityGroup['IpPermissions']
                for ipPermission in ipPermissions:
                    groupType = 'ingress'
                    printSecGroup (groupType, ipPermission)
                ipPermissionsEgress = securityGroup['IpPermissionsEgress']
                for ipPermissionEgress in ipPermissionsEgress:
                    groupType = 'egress'
                    printSecGroup (groupType, ipPermissionEgress)

        #boto3 library ec2 API descrive VPC
        VPCs = ec2con.describe_vpcs().get('Vpcs')
        if len(VPCs) > 0:
            csv_file.write("%s,%s,%s,%s,%s\n"%('','','','',''))
            csv_file.write("%s,%s\n"%('VPC',regname))
            csv_file.write("%s,%s,%s,%s,%s\n"%('VpcId','InstanceTenancy','State','CidrBlock','Tags'))
            csv_file.flush()
            for vpc in VPCs:
                vpcid=vpc['VpcId']
                instancetenancy=vpc['InstanceTenancy']
                state=vpc['State']
                cidr=vpc['CidrBlock']
                tags=vpc.get('Tags','notag')
                csv_file.write("%s,%s,%s,%s,%s\n"%(vpcid,instancetenancy,state,cidr,tags))
                csv_file.flush()

        #
        # RDS and other databases
        #
        rdscon = session.client('rds',region_name=reg)

        #boto3 library RDS API describe db instances page
        #http://boto3.readthedocs.org/en/latest/reference/services/rds.html#RDS.Client.describe_db_instances
        rdb = rdscon.describe_db_instances().get(
        'DBInstances',[]
        )
        rdblist = len(rdb)
        if rdblist > 0:
            csv_file.write("%s,%s,%s,%s\n" %('','','',''))
            csv_file.write("%s,%s\n"%('RDS INSTANCE',regname))
            csv_file.write("%s,%s,%s,%s\n" %('DBInstanceIdentifier','DBInstanceStatus','DBName','DBInstanceClass'))
            csv_file.flush()

        for dbinstance in rdb:
            DBInstanceIdentifier = dbinstance['DBInstanceIdentifier']
            DBInstanceClass = dbinstance['DBInstanceClass']
            DBInstanceStatus = dbinstance['DBInstanceStatus']
            try:
                DBName = dbinstance['DBName']
            except:
                DBName = "empty"
            csv_file.write("%s,%s,%s,%s\n" %(DBInstanceIdentifier,DBInstanceStatus,DBName,DBInstanceClass))
            csv_file.flush()

        #boto3 library dynamoDB API describe_table page
        #http://boto3.readthedocs.io/en/latest/reference/services/dynamodb.html#DynamoDB.Client.describe_table
        dynamodb = session.client('dynamodb',region_name=reg)
        ddblist = dynamodb.list_tables().get('TableNames', [])
        if len(ddblist) > 0:
            csv_file.write("%s,%s,%s,%s\n" %('','','',''))
            csv_file.write("%s,%s\n"%('DYNAMODB TABLES',regname))
            csv_file.write("%s,%s,%s\n" %('TableName','TableSizeBytes','ItemCount'))
            csv_file.flush()
            for table in ddblist:
                desctable = dynamodb.describe_table(TableName=table)['Table']
                csv_file.write("%s,%s,%s\n" %(desctable['TableName'],desctable['TableSizeBytes'],desctable['ItemCount']))
                csv_file.flush()                

        #ELB connection beginning
        elbcon = session.client('elb',region_name=reg)

        #boto3 library ELB API describe load balancer instances page
        #http://boto3.readthedocs.org/en/latest/reference/services/elb.html#ElasticLoadBalancing.Client.describe_load_balancers
        loadbalancer = elbcon.describe_load_balancers().get('LoadBalancerDescriptions',[])
        loadbalancerlist = len(loadbalancer)
        if loadbalancerlist > 0:
            csv_file.write("%s,%s,%s,%s\n" % ('','','',''))
            csv_file.write("%s,%s\n"%('ELB INSTANCE',regname))
            csv_file.write("%s,%s,%s,%s\n" % ('LoadBalancerName','DNSName','CanonicalHostedZoneName','CanonicalHostedZoneNameID'))
            csv_file.flush()

        for load in loadbalancer:
            LoadBalancerName=load['LoadBalancerName']
            DNSName=load['DNSName']
            CanonicalHostedZoneName=load['CanonicalHostedZoneName']
            CanonicalHostedZoneNameID=load['CanonicalHostedZoneNameID']
            csv_file.write("%s,%s,%s,%s\n" % (LoadBalancerName,DNSName,CanonicalHostedZoneName,CanonicalHostedZoneNameID))
            csv_file.flush()

#
# International Resources (no region)
#
regname='global'

#
# S3 quick inventory
#
s3i = session.client('s3')
#http://boto3.readthedocs.io/en/latest/reference/services/s3.html#client
listbuckets = s3i.list_buckets().get('Buckets')
if len(listbuckets) > 0:
    csv_file.write("%s,%s,%s,%s\n" % ('','','',''))
    csv_file.write("%s :%s\n"%('S3 BUCKETS',regname))
    csv_file.write("%s,%s,%s,%s\n" % ('Name','Nb objects','Size','Has Website'))
    csv_file.flush()
    for bucket in listbuckets:
        #http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.list_objects_v2
        bucketname = bucket['Name']
        # Check if a website if configured; if yes, it could lead to a DLP issue
        has_website = 'unknown'
        try:
            website = s3i.get_bucket_website(Bucket=bucketname)
            has_website = 'yes'
        except ClientError as ce:
            if 'NoSuchWebsiteConfiguration' in ce.args[0]:
                has_website = 'no'
        # Summarize nb of objets and total size (for the current bucket)
        paginator = s3i.get_paginator('list_objects_v2')
        nbobj = 0
        size = 0
        page_objects = paginator.paginate(Bucket=bucketname,PaginationConfig={'MaxItems': 10})
        for objects in page_objects:
            nbobj += len(objects['Contents'])
            for obj in objects['Contents']:
                size += obj['Size']
        csv_file.write("%s,%s,%s,%s\n" % (bucketname,nbobj,size,has_website))
        csv_file.flush()

#
# IAM inventory
#
iam = session.client('iam')
#http://boto3.readthedocs.io/en/latest/reference/services/iam.html
listusers = iam.list_users().get('Users')
csv_file.write("%s,%s,%s,%s\n" % ('','','',''))
csv_file.write("%s :%s\n"%('IAM USERS',regname))
csv_file.write("%s,%s\n" % ('Name','Groups'))
csv_file.flush()
for user in listusers:
    username = user['UserName']
    #http://boto3.readthedocs.io/en/latest/reference/services/iam.html#IAM.Client.list_groups_for_user
    groups = iam.list_groups_for_user(UserName=user['UserName'])
    user_groups = []
    for group in groups.get('Groups'):
        user_groups.append(group.get('Arn'))
    csv_file.write("%s,%s\n" % (username, user_groups))
    csv_file.flush()

        
#http://boto3.readthedocs.io/en/latest/reference/services/iam.html#role    
roles = iam.list_roles()
csv_file.write("%s,%s,%s,%s\n" % ('','','',''))
csv_file.write("%s :%s\n"%('IAM ROLES',regname))
csv_file.write("%s\n" % ('RoleName'))
csv_file.flush()
#pprint.pprint(roles)
for role in roles.get('Roles'):
    csv_file.write("%s\n" % (role['RoleName']))
            
# Results
csv_file.close()
date_fmt = strftime("%Y_%m_%d", gmtime())
#Give your file path
filepath ='AWS_Resources_' + date_fmt + '.csv'
#Save Inventory
##s3.Object(S3_INVENTORY_BUCKET, filename).put(Body=open(filepath, 'rb'))
