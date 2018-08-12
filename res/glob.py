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

def get_inventory(ownerId, aws_service, aws_region, function_name, key_get = "", detail_function = "", join_key = "", detail_join_key = "", detail_get_key = ""):

    # aws_region = all, global

    inventory = []
    config.logger.info('Account {}, {} inventory ({})'.format(ownerId, aws_service, aws_region))

    if (aws_region == 'all'):

        # inventory must be processed region by region
        for region in config.regions:
            try:
                region_name = region['RegionName']
                config.logger.info('Account {}, {} inventory for region {}'.format(ownerId, aws_service, region_name))
                utils.display(ownerId, region_name, aws_service, function_name)
                client = boto3.client(aws_service, region_name)
                inv_list = client.__getattribute__(function_name)().get(key_get)
                for inv in inv_list:
                    detailed_inv = get_inventory_detail(client, region_name, inv, detail_function, join_key, detail_join_key, detail_get_key)
                    inventory.append(json.loads(utils.json_datetime_converter(detailed_inv)))
            except (botocore.exceptions.EndpointConnectionError, botocore.exceptions.ClientError):
                # unsupported region for efs
                config.logger.warning("{} is not available (not supported?) in region {}.".format(aws_service, region_name))

    elif (aws_region == 'global'):

        # inventory can be globalized
        try:
            client = boto3.client(aws_service)
            config.logger.info('Account {}, {} inventory for region \'{}\''.format(ownerId, aws_service, aws_region))
            utils.display(ownerId, aws_region, aws_service, function_name)
            inv_list = client.__getattribute__(function_name)().get(key_get)
            for inv in inv_list:
                detailed_inv = get_inventory_detail(client, aws_region, inv, detail_function, join_key, detail_join_key, detail_get_key)
                inventory.append(json.loads(utils.json_datetime_converter(detailed_inv)))
        except (botocore.exceptions.EndpointConnectionError, botocore.exceptions.ClientError):
            # unsupported region for efs
            config.logger.warning("A problem occurred or {} is not not supported.".format(aws_service))        

    else:

        # arghhhhh
        config.logging.error('Very bad trip: get_inventory called with improper arguments (aws_region={}).'.format(aws_region))

    return inventory


def get_inventory_detail(client, region_name, inv, detail_function, join_key, detail_join_key, detail_get_key):

    # a revoir à cause des paramètres à rajouter, pour la sélection (param) et pour le get (qui poeut être nul ou différent de ce qui a été utilisé)
    # tests : KMS, codestar
    # liste : get_key
    # detail : join_key, detail_join_key, detail_get_key

    if (detail_function != ""):
        if (isinstance(inv, str)):
            key = inv
        else:
            key = inv.get(join_key)
        param = {detail_join_key: key} # works only for a single value, but some functions needs tables[], like ECS Tasks
        if (detail_get_key != ""):
            detailed_inv = client.__getattribute__(detail_function)(**param).get(detail_get_key)
        else:
            detailed_inv = client.__getattribute__(detail_function)(**param)
            if ("ResponseMetadata" in detailed_inv):
                del detailed_inv['ResponseMetadata']
    else:
        detailed_inv = inv

    if ('RegionName' not in detailed_inv):
        detailed_inv['RegionName'] = region_name

    return detailed_inv


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')