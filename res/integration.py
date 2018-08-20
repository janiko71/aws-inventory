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
#    Simple Queue Service. Not sure that the API works well (strange responses in aws cli)
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


#  ------------------------------------------------------------------------
#
#    Amazon MQ
#
#  ------------------------------------------------------------------------

def get_mq_inventory(oId):

    """
        Returns Amazon MQ details

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: Amazon MQ inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/mq.html
    """ 

    mq_inventory = {}
    
    mq_inventory['brokers'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "mq", 
        aws_region = "all", 
        function_name = "list_brokers", 
        key_get = "BrokerSummaries",
        detail_function = "describe_broker", 
        join_key = "BrokerId", 
        detail_join_key = "BrokerId", 
        detail_get_key = ""
    )

    mq_inventory['configurations'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "mq", 
        aws_region = "all", 
        function_name = "list_configurations", 
        key_get = "Configurations",
        detail_function = "describe_configuration", 
        join_key = "Id", 
        detail_join_key = "ConfigurationId", 
        detail_get_key = ""
    )
    
    return mq_inventory

#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')