import boto3
import botocore
import json
import config
import res.utils as utils


#  ------------------------------------------------------------------------
#
#     The MOST important function of that project: generic inventory
#
#  ------------------------------------------------------------------------

def get_inventory(aws_service, aws_region, function_name, param, key_get):

    # aws_region = all, global

    inventory = []
    config.logger.info('{} inventory ({})'.format(aws_service, aws_region))

    if (aws_region == 'all'):

        # inventory must be processed region by region
        for region in config.regions:
            region_name = region['RegionName']
            config.logger.info('{} inventory for region {}'.format(aws_service, region_name))
            utils.display("", region_name, aws_service)
            client = boto3.client(aws_service, region_name)
            inv_list = client.__getattribute__(function_name)().get(key_get)
            for inv in inv_list:
                inventory.append(json.loads(utils.json_datetime_converter(inv)))

    elif (aws_region == 'global'):

        # inventory can be globalized
        client = boto3.client(aws_service)
        config.logger.info('{} inventory for region \'{}\''.format(aws_service, aws_region))
        utils.display("", region_name, aws_service)
        inv_list = client.__getattribute__(function_name)().get(key_get)
        for inv in inv_list.get(key_get):
            inventory.append(json.loads(utils.json_datetime_converter(inv)))

    else:

        # arghhhhh
        config.logging.error('Very bad trip: get_inventory called with improper arguments (aws_region={}).'.format(aws_region))

    return inventory


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')