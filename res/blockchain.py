import boto3
import botocore
import json
import config
import pprint, operator
import res.utils as utils
import res.glob as glob

# =======================================================================================================================
#
#  Supported services   : Amazon Managed Blockchain, Amazon Quantum Ledger Database (QLDB)
#  Unsupported services : None
#
# =======================================================================================================================

#  ------------------------------------------------------------------------
#
#    Amazon Managed Blockchain
#
#  ------------------------------------------------------------------------

def get_managed_blockchain_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns Managed Blockchain inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: Managed Blockchain inventory
        :rtype: json

        ..note:: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/managedblockchain.html
    """

    inventory = {}

    inventory['networks'] = glob.get_inventory(
        ownerId=oId,
        profile=profile,
        boto3_config=boto3_config,
        selected_regions=selected_regions,
        aws_service="managedblockchain",
        aws_region="all",
        function_name="list_networks",
        key_get="Networks"
    )

    return inventory

#  ------------------------------------------------------------------------
#
#    Amazon Quantum Ledger Database (QLDB)
#
#  ------------------------------------------------------------------------
 
def get_qldb_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns QLDB inventory

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: QLDB inventory
        :rtype: json

        ..note:: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/qldb.html
    """

    inventory = {}

    inventory['ledgers'] = glob.get_inventory(
        ownerId=oId,
        profile=profile,
        boto3_config=boto3_config,
        selected_regions=selected_regions,
        aws_service="qldb",
        aws_region="all",
        function_name="list_ledgers",
        key_get="Ledgers",
        detail_function="describe_ledger",
        join_key="Name",
        detail_join_key="Name",
        detail_get_key="",
        pagination=False,
        pagination_detail=False,
    )

    return inventory