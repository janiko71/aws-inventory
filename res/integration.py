import boto3
import botocore
import json
import config
import pprint, operator
import res.utils as utils
import res.glob as glob

# =======================================================================================================================
#
#  Supported services   : Amazon MQ, Simple Notification Service (SNS), Simple Queue Service (SQS), Step functions,
#                         Amazon AppFlow, Amazon EventBridge SWF
#  Unsupported services : Apache Airflow 
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

    
#  ------------------------------------------------------------------------
#
#    Appflow
#
#  ------------------------------------------------------------------------

def get_appflow_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns appflow (flows, connectors) details

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: appflow (flows, connectors) inventory
        :rtype: json

        ..note:: not documented yet
    """ 

    inventory = {}
    
    inventory['flows'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "appflow", 
        aws_region = "all", 
        function_name = "list_flows", 
        key_get = "flows",
        detail_function = "describe_flow",
        join_key = "flowName",
        detail_join_key = "flowName",
        detail_get_key = "",
        pagination_detail = False,
        pagination = False
    )
    
    return inventory

    
#  ------------------------------------------------------------------------
#
#    EventBridge (archives, connections, event_buses, event_sources, replays, rules)
#
#  ------------------------------------------------------------------------

def get_eventbridge_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns EventBridge (rules) details

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: EventBridge (rules) inventory
        :rtype: json

        ..note:: not documented yet
    """ 

    inventory = {}

    inventory['archives'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "events", 
        aws_region = "all", 
        function_name = "list_archives", 
        key_get = "Archives",
        detail_function = "describe_archive",
        join_key = "ArchiveName",
        detail_join_key = "ArchiveName",
        detail_get_key = "",
        pagination_detail = False,
        pagination = False
    )

    inventory['connections'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "events", 
        aws_region = "all", 
        function_name = "list_connections", 
        key_get = "Connections",
        detail_function = "describe_connection",
        join_key = "Name",
        detail_join_key = "Name",
        detail_get_key = "",
        pagination_detail = False,
        pagination = False
    )

    inventory['event_buses'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "events", 
        aws_region = "all", 
        function_name = "list_event_buses", 
        key_get = "EventBuses",
        detail_function = "describe_event_bus",
        join_key = "Name",
        detail_join_key = "Name",
        detail_get_key = "",
        pagination_detail = False,
        pagination = False
    )
 
    inventory['event_sources'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "events", 
        aws_region = "all", 
        function_name = "list_event_sources", 
        key_get = "EventSources",
        detail_function = "describe_event_source",
        join_key = "Name",
        detail_join_key = "Name",
        detail_get_key = "",
        pagination_detail = False,
        pagination = False
    )
    
    inventory['replays'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "events", 
        aws_region = "all", 
        function_name = "list_replays", 
        key_get = "ReplayName",
        detail_function = "describe_replay",
        join_key = "Name",
        detail_join_key = "ReplayName",
        detail_get_key = "",
        pagination_detail = False,
        pagination = False
    )
      
    inventory['rules'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "events", 
        aws_region = "all", 
        function_name = "list_rules", 
        key_get = "Rules",
        detail_function = "describe_rule",
        join_key = "Name",
        detail_join_key = "Name",
        detail_get_key = "",
        pagination_detail = False,
        pagination = False
    )
    
    return inventory


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')