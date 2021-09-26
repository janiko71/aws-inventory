import boto3
import botocore
import json
import config
import pprint, operator
import res.utils as utils
import res.glob as glob

# =======================================================================================================================
#
#  Supported services   : Elasticsearch Service, CloudSearch, Data Pipeline, EMR
#  Unsupported services : Athena, Kinesis, Quicksight (not scriptable), Glue
#
# =======================================================================================================================

#  ------------------------------------------------------------------------
#
#    Elasticsearch
#
#  ------------------------------------------------------------------------

def get_es_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns Elasticsearch details

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: Elasticsearch inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/es.html
    """ 
    
    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "es", 
        aws_region = "all", 
        function_name = "list_domain_names", 
        key_get = "DomainNames",
        join_key = "DomainName",
        detail_join_key = "DomainName",
        detail_function = "describe_elasticsearch_domain",
        detail_get_key = "DomainStatus"
    )


#  ------------------------------------------------------------------------
#
#    Cloudsearch
#
#  ------------------------------------------------------------------------

def get_cloudsearch_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns cloudsearch details

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string        

        :return: cloudsearch inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/cloudsearch.html
    """ 
    
    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "cloudsearch", 
        aws_region = "all", 
        function_name = "describe_domains", 
        key_get = "DomainStatusList"
    )


#  ------------------------------------------------------------------------
#
#    Data Pipeline
#
#  ------------------------------------------------------------------------

def get_datapipeline_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns datapipeline details

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: datapipeline inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/datapipeline.html
    """ 
    
    return glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "datapipeline", 
        aws_region = "all", 
        function_name = "list_pipelines", 
        key_get = "pipelineIdList",
        pagination = True,
        join_key = "id",
        detail_join_key = "pipelineId",
        detail_function = "get_pipeline_definition",
        detail_get_key = ""
    )


#  ------------------------------------------------------------------------
#
#    Elastic MapReduce
#
#  ------------------------------------------------------------------------

def get_emr_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns emr details

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: emr inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/emr.html
    """ 
    
    emr_inventory = {}

    emr_inventory['clusters'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "emr", 
        aws_region = "all", 
        function_name = "list_clusters", 
        key_get = "Clusters",
        pagination = True,
        join_key = "Id",
        detail_join_key = "ClusterId",
        detail_function = "describe_cluster",
        detail_get_key = ""
    )
    
    emr_cluster = {}

    if (len(emr_inventory['clusters']) > 0):

        for cluster in emr_inventory['clusters']:
            
            emr_cluster['fleets'] = glob.get_inventory(
                ownerId = oId,
                profile = profile,
                boto3_config = boto3_config,
                selected_regions = selected_regions,
                aws_service = "emr", 
                aws_region = "all", 
                function_name = "list_instance_fleets", 
                key_get = "InstanceFleets",
                additional_parameters = {'ClusterId': cluster['Id']}
            )

            emr_cluster['instance_groups'] = glob.get_inventory(
                ownerId = oId,
                profile = profile,
                boto3_config = boto3_config,
                selected_regions = selected_regions,
                aws_service = "emr", 
                aws_region = "all", 
                function_name = "list_instance_groups", 
                key_get = "InstanceGroups",
                pagination = True,
                join_key = "Id",
                detail_join_key = "ClusterId",
                detail_function = "describe_cluster",
                detail_get_key = ""
            )

    else:

        config.nb_units_done = config.nb_units_done + 2 * config.nb_regions

    emr_inventory['clusters'] = emr_cluster

    return emr_inventory

#
# Hey, doc: we're in a module!
#
if (__name__ == "__main__"):
    print("Module => Do not execute")