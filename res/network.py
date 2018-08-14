import boto3
import botocore
import json
import config
import res.utils as utils
import res.glob  as glob

# =======================================================================================================================
#
#  Supported services   : API Gateway (simple), VPC (in 'compute' module)
#  Unsupported services : Route 53, Cloud Front, Direct Connect
#
# =======================================================================================================================


#  ------------------------------------------------------------------------
#
#    API Gateway (simple) 
#
#  ------------------------------------------------------------------------

def get_apigateway_inventory(oId):

    """
        Returns API Gateway inventory

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: API Gateway inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/apigateway.html
        ..todo:: add --> plans, api keys, custom domain names, client certificates, vpc links
    """
    
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "apigateway", 
        aws_region = "all", 
        function_name = "get_rest_apis", 
        key_get = "items"
    )


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')