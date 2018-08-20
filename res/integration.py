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
#  Unsupported services : Step functions, Amazon MQ, Simple Notification Service (SNS), Simple Queue Service (SQS), SWF
#
# =======================================================================================================================

#  ------------------------------------------------------------------------
#
#    Simple Queue Service
#
#  ------------------------------------------------------------------------

def get_sqs_inventory(oId):

    """
        Returns Simple Queue Service (SQS) details

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: Simple Queue Service (SQS) inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/sqs.html
    """ 
    
    return glob.get_inventory(
        ownerId = oId,
        aws_service = "sqs", 
        aws_region = "all", 
        function_name = "list_queues", 
        key_get = "QueueUrls",
        detail_function = "get_queue_attributes", 
        join_key = "QueueUrl", 
        detail_join_key = "QueueUrl", 
        detail_get_key = "Attributes"
    )


#
# Hey, doc: we're in a module!
#
#if (__name__ == '__main__'):
#    print('Module => Do not execute')