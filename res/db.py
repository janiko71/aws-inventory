import boto3
import botocore
import json
import config
import res.utils as utils
import res.glob  as glob

# =======================================================================================================================
#
#  Supported services   : RDS, DynamoDB, ElastiCache, Neptune, Amazon Redshift
#  Unsupported services : None
#
# =======================================================================================================================

#  ------------------------------------------------------------------------
#
#    RDS 
#
#  ------------------------------------------------------------------------

def get_rds_inventory(oId):

    """
        Returns RDS inventory

        :param oId: ownerId (AWS account)
        :type oId: string


        :return: RDS inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/rds.html

    """

    return glob.get_inventory(
        ownerId = oId,
        aws_service = "rds", 
        aws_region = "all", 
        function_name = "describe_db_instances", 
        key_get = "DBInstances",
        pagination = True
    )


#  ------------------------------------------------------------------------
#
#    DynamoDB 
#
#  ------------------------------------------------------------------------

def get_dynamodb_inventory(oId):

    """
        Returns dynamoDB inventory

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: dynamoDB inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/dynamodb.html

    """

    return glob.get_inventory(
        ownerId = oId,
        aws_service = "dynamodb", 
        aws_region = "all", 
        function_name = "list_tables", 
        key_get = "TableNames",
        detail_function = "describe_table", 
        join_key = "TableName", 
        detail_join_key = "TableName", 
        detail_get_key = "Table",
        pagination = True
    )


#  ------------------------------------------------------------------------
#
#    Neptune 
#
#  ------------------------------------------------------------------------

def get_neptune_inventory(oId):

    """
        Returns neptune inventory (instances & clusters). Instances are listed in RDS inventory.

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: neptune inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/neptune.html

    """

    neptune_inventory = {}

    neptune_inventory['clusters'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "neptune", 
        aws_region = "all", 
        function_name = "describe_db_clusters", 
        key_get = "DBClusters"
    )

    return neptune_inventory
   

#  ------------------------------------------------------------------------
#
#    ElastiCache
#
#  ------------------------------------------------------------------------

def get_elasticache_inventory(oId):

    """
        Returns elasticache inventory (instances & clusters). Instances are listed in RDS inventory.

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: elasticache inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/elasticache.html

    """

    elasticache_inventory = {}

    elasticache_inventory['cache-clusters'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "elasticache", 
        aws_region = "all", 
        function_name = "describe_cache_clusters", 
        key_get = "CacheClusters",
        pagination = True
    )

    elasticache_inventory['reserved-cache-nodes'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "elasticache", 
        aws_region = "all", 
        function_name = "describe_reserved_cache_nodes", 
        key_get = "ReservedCacheNodes",
        pagination = True
    )

    return elasticache_inventory
   

#  ------------------------------------------------------------------------
#
#    Redshift
#
#  ------------------------------------------------------------------------

def get_redshift_inventory(oId):

    """
        Returns redshift inventory (instances & clusters). Instances are listed in RDS inventory.

        :param oId: ownerId (AWS account)
        :type oId: string

        :return: redshift inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/redshift.html

    """

    redshift_inventory = {}

    redshift_inventory['clusters'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "redshift", 
        aws_region = "all", 
        function_name = "describe_clusters", 
        key_get = "Clusters",
        pagination = True
    )

    redshift_inventory['reserved-nodes'] = glob.get_inventory(
        ownerId = oId,
        aws_service = "redshift", 
        aws_region = "all", 
        function_name = "describe_reserved_nodes", 
        key_get = "ReservedNodes",
        pagination = True
    )

    return redshift_inventory


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')