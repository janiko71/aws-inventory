import boto3
import botocore
import json
import config
import res.utils as utils


#  ------------------------------------------------------------------------
#
#    Cost explorer (ce) ==> Still experimental!
#
#  ------------------------------------------------------------------------

def get_ce_inventory(ownerId, values):

    """
        Returns cost inventory, for a period (1 month ?)

        :param ownerId: ownerId (AWS account)
        :type ownerId: string
        :param region_name: region name
        :type region_name: string

        :return: RDS inventory
        :rtype: json

        :Example:

        b.get_cost_and_usage(TimePeriod={'Start': '2018-07-01','End': '2018-07-31'},Granularity='DAILY',Metrics=('AmortizedCost' , 'BlendedCost' , 'UnblendedCost' , 'UsageQuantity'))
        b.get_cost_and_usage(TimePeriod={'Start': '2018-01-01','End': '2018-08-31'},Granularity='MONTHLY',Metrics=('AmortizedCost' , 'BlendedCost' , 'UnblendedCost' , 'UsageQuantity')

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/rds.html

    """
    
    config.logger.info('RDS inventory, all regions, get_rds_inventory')

    client = boto3.client('ce')
    ce_list = client.get_cost_and_usage(
        TimePeriod={'Start': '2018-01-01','End': '2018-08-31'},
        Granularity='MONTHLY',
        Metrics=('AmortizedCost' , 'BlendedCost' , 'UnblendedCost' , 'UsageQuantity')
    )

    return ce_list


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')