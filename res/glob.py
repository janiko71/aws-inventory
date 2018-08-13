import boto3
import botocore
import json
import config
import res.utils as utils


#  ------------------------------------------------------------------------
#
#     The MOST important functions of that project: generic inventory
#
#  ------------------------------------------------------------------------

def get_inventory(ownerId, aws_service, aws_region, function_name, key_get = "", detail_function = "", join_key = "", detail_join_key = "", detail_get_key = ""):
    """
        Returns inventory for a service. It's a generic function, meaning that it should work for almost any AWS service,
        except for specialized ones or for those who don't have AWS CLI/SDK equivalent. 
        
        The list of parameters is impressive but it allows to add a service in minutes without any re-coding (just testing!)

        :param ownerId: ownerId (AWS account). Mandatory.
        :param aws_service: name of AWS service (= the name used in SDK, and defined in config.py). Mandatory.
        :param aws_region: scope of the inventory, depending on the service. Some are globalized, some needs to be executed in every AWS region. Mandatory.
        :param function_name: the name of the SDK function to call to get inventory (or the list of resources). Mandatory.
        :param key_get: the key containing information about the resource, when SDK returns a dict. Optional.
        :param detail_function: the SDK function to call to get details, if needed. Optional.
        :param join_key: Id of the resource you for which you want details.
        :param detail_join_key: When needed, field name of the paramater to include in de detail_function to get the right resource instance.
        :param detail_get_key: the key containing detailed information about the resource, when SDK returns a dict. Optional.

        :type ownerId: string
        :type aws_service: string
        :type aws_region: string
        :type function_name: string
        :type key_get: string
        :type detail_function: string
        :type join_key: string
        :type detail_join_key: string
        :type detail_get_key: string        

        :return: neptune inventory
        :rtype: json

        ..note:: http://boto3.readthedocs.io/en/latest/reference/services/neptune.html

    """
    # aws_region = all, global

    inventory = []
    config.logger.info('Account {}, {} inventory ({})'.format(ownerId, aws_service, aws_region))

    if (aws_region == 'all'):

        # inventory must be processed region by region
        for region in config.regions:
            try:
                region_name = region['RegionName']
                utils.progress(region_name)
                config.logger.info('Account {}, {} inventory for region {}'.format(ownerId, aws_service, region_name))
                client = boto3.client(aws_service, region_name)
                inv_list = client.__getattribute__(function_name)().get(key_get)
                utils.display(ownerId, region_name, aws_service, function_name)
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
            utils.progress(aws_region)
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

    '''
        Get details for the resource, if needed. Same parameters as get_detail but all are mandatory except detail_get_key

        .. seealso:: :function:`get_inventory`
    '''

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