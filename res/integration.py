import boto3
import botocore
import json
import config
import pprint, operator
import res.utils as utils
import res.glob as glob

# =======================================================================================================================
#
#  Supported services   : Amazon MQ, Simple Notification Service (SNS), Simple Queue Service (SQS), 
#  Unsupported services : Step functions, SWF
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
        key_get = "Configurations"
    )
    
    return mq_inventory


#  ------------------------------------------------------------------------
#
#    Simple Notification Service (SNS)
#
#  ------------------------------------------------------------------------

def get_sns_inventory(oId):

    """
        Returns sns (topics, applications) details

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: Amazon sns inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/sns.html
    """ 

    sns_inventory = {}
    
    sns_inventory['topics'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "sns", 
        aws_region = "all", 
        function_name = "list_topics", 
        key_get = "Topics",
        pagination = True
    )

    sns_inventory['applications'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "sns", 
        aws_region = "all", 
        function_name = "list_platform_applications", 
        key_get = "PlatformApplications",
        pagination = True
    )
    
    return sns_inventory


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')