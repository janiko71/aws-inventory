import boto3
import botocore
import json
import config
import pprint, operator
import res.utils as utils
import res.glob as glob

# =======================================================================================================================
#
#  Supported services   : None
#  Unsupported services : Athena, EMR, CloudSearch, Elasticsearch Service, Kinesis, Quicksight, Data Pipeline, Glue
#
# =======================================================================================================================

#  ------------------------------------------------------------------------
#
#    XXX
#
#  ------------------------------------------------------------------------

def get_xxx_inventory(oId):

    """
        Returns xxx details

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: xxx inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/xxx.html
    """ 
    
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "xxx", 
        aws_region = "all", 
        function_name = "list_projects", 
        key_get = "projects",
        detail_function = "describe_project", 
        join_key = "projectId", 
        detail_join_key = "id", 
        detail_get_key = ""
    )


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')