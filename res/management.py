import boto3
import botocore
import json
import config
import res.utils as utils
import res.glob  as glob

# =======================================================================================================================
#
#  Supported services   : None
#  Unsupported services : CloudTrail, CloudWtach, AWS Auto Scaling, CloudFormation, Config, OpsWork, Service Catalog, Systems Manager, Trusted Advisor, Managed Services
#
# =======================================================================================================================


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')