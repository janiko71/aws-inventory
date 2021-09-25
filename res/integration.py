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
#  Unsupported services : Amazon AppFlow, Amazon EventBridge, Step functions, SWF, Apache Airflow 
#
# =======================================================================================================================

#  ------------------------------------------------------------------------
#
#    Simple Queue Service. Not sure that the API works well (strange responses in aws cli)
#
#  ------------------------------------------------------------------------

def get_sqs_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns Simple Queue Service (SQS) details

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: Simple Queue Service (SQS) inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/sqs.html
    """ 
    
    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
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

def get_mq_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns Amazon MQ details

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: Amazon MQ inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/mq.html
    """ 

    mq_inventory = {}
    
    mq_inventory['brokers'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
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
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
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

def get_sns_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns sns (topics, applications) details

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: Amazon sns inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/sns.html
    """ 

    sns_inventory = {}
    
    sns_inventory['topics'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "sns", 
        aws_region = "all", 
        function_name = "list_topics", 
        key_get = "Topics",
        pagination = True
    )

    sns_inventory['applications'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "sns", 
        aws_region = "all", 
        function_name = "list_platform_applications", 
        key_get = "PlatformApplications",
        pagination = True
    )
#  ------------------------------------------------------------------------
#
#    Step functions
#
#  ------------------------------------------------------------------------

def get_stepfunctions_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns stepfunctions (machines, activities) details

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: stepfunctions (machines, activities) inventory
        :rtype: json

        ..note:: not documented yet
    """ 

    inventory = {}
    
    inventory['machines'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "stepfunctions", 
        aws_region = "all", 
        function_name = "list_state_machines", 
        key_get = "stateMachines",
        detail_function = "describe_state_machine",
        join_key = "stateMachineArn",
        detail_join_key = "stateMachineArn",
        detail_get_key = "",
        pagination_detail = False,
        pagination = True
    )

    inventory['activities'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "stepfunctions", 
        aws_region = "all", 
        function_name = "list_activities", 
        key_get = "activities",
        pagination = True
    )
    
    return inventory


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')