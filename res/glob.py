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

def get_inventory(ownerId, 
                  aws_service, 
                  aws_region, 
                  function_name, 
                  key_get = "", 
                  detail_function = "", 
                  join_key = "", 
                  detail_join_key = "", 
                  detail_get_key = "",
                  pagination = False,
                  pagination_detail = False):

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
        :param pagination: tells if the inventory function supports pagination or not ; pagination is need for large inventory lists.
        :param pagination_detail: tells if the detail inventory function supports pagination or not ; pagination is need for large inventory lists.

        :type ownerId: string
        :type aws_service: string
        :type aws_region: string
        :type function_name: string
        :type key_get: string
        :type detail_function: string
        :type join_key: string
        :type detail_join_key: string
        :type detail_get_key: string 
        :type pagination: boolean
        :type pagination_detail: boolean       

        :return: inventory
        :rtype: json

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

                if (pagination):

                    paginator = client.get_paginator(function_name)
                    page_iterator = paginator.paginate()
                    utils.display(ownerId, region_name, aws_service, function_name)

                    for detail in page_iterator:
                        for inventory_object in detail.get(key_get):
                            detailed_inv = get_inventory_detail(client, region_name, inventory_object, detail_function, join_key, detail_join_key, detail_get_key)
                            inventory.append(json.loads(utils.json_datetime_converter(detailed_inv)))
                
                else:

                    inv_list = client.__getattribute__(function_name)().get(key_get)
                    utils.display(ownerId, region_name, aws_service, function_name)
                    for inventory_object in inv_list:
                       detailed_inv = get_inventory_detail(client, region_name, inventory_object, detail_function, join_key, detail_join_key, detail_get_key)
                       inventory.append(json.loads(utils.json_datetime_converter(detailed_inv)))

            except (botocore.exceptions.EndpointConnectionError, botocore.exceptions.ClientError) as e:

                # unsupported region for efs
                config.logger.warning("{} is not available (not supported?) in region {}.".format(aws_service, region_name))
                config.logger.debug("Error text : {}".format(e))

            except Exception as e:

                config.logger.error("Error while processing {}, {}.\n{}".format(aws_service, region_name, e))

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

        except (botocore.exceptions.EndpointConnectionError, botocore.exceptions.ClientError) as e:

            # unsupported region (or bad coding somewhere)
            config.logger.warning("A problem occurred or {} is not not supported.".format(aws_service))        
            config.logger.debug("Error text : {}".format(e))

        except Exception as e:

            config.logger.error("Error while processing {}, {}.\n{}".format(aws_service, aws_region, e))

    else:

        # arghhhhh
        config.logging.error('Very bad trip: get_inventory called with improper arguments (aws_region={}).'.format(aws_region))

    return inventory


def get_inventory_detail(client, 
                         region_name, 
                         inventory_object, 
                         detail_function, 
                         join_key, 
                         detail_join_key, 
                         detail_get_key, 
                         pagination_detail = False):

    '''
        Get details for the resource, if needed. Same parameters as get_detail but all are mandatory except detail_get_key and pagination_detail

        .. seealso:: :function:`get_inventory`
    '''

    config.logger.info('{} detail function'.format(detail_function))
    detailed_inv = inventory_object

    # if no function is provided, not detail is needed

    if (detail_function != ""):

        # we set the key value; it's something that identifies the objet and that we pass to 
        # the detail function as a search key. Sometimes the upper inventory functions returns 
        # full objects, and sometime only a list of id. That's why we test if we have an objet
        # or only a string passed as parameter.s

        if (isinstance(inventory_object, str)):
            # the upper inventory function returned str
            detailed_inv = {detail_get_key: inventory_object}
            key = inventory_object
        else:
            # normal objet; we retrieve the value of the 'join key' field
            key = inventory_object.get(join_key)

        param = {detail_join_key: key} # works only for a single value, but some functions needs tables[], like ECS Tasks

        # now we fetch the details; again, depending on the called function, the return object may contains
        # a list, an object, etc. The return value structure may vary a lot.

        if (detail_get_key != ""):

            # here a detail_get_ket is provided to get the right object, in the JSON response
            if (pagination_detail):
                # in case that the detail function allows pagination, for large lists
                paginator = client.get_paginator(detail_function)
                page_iterator = paginator.paginate(**param)
                for detail in page_iterator:
                    for detail_object in detail.get(detail_get_key):
                        detailed_inv[detail_get_key].append(detail_object)
            else:
                # no pagination, so we call the detail function directly
                detailed_inv[detail_get_key] = client.__getattribute__(detail_function)(**param).get(detail_get_key)

        else:

            # well, here there's no key, we return the object as is. 
            detail_get_key = 'details'

            # here a detail_get_ket is provided to get the right object, in the JSON response
            if (pagination_detail):
                # in case that the detail function allows pagination, for large lists
                paginator = client.get_paginator(detail_function)
                page_iterator = paginator.paginate(**param)
                for detail in page_iterator:
                    for detail_object in detail:
                        detailed_inv[detail_get_key].append(detail_object)
            else:
                # no pagination, so we call the detail function directly
                detailed_inv[detail_get_key] = client.__getattribute__(detail_function)(**param)

        if ("ResponseMetadata" in detailed_inv[detail_get_key]):
            del detailed_inv[detail_get_key]['ResponseMetadata']

    # Sometimes we loose region name; if so, we add it 
    if ('RegionName' not in detailed_inv):
        detailed_inv['RegionName'] = region_name

    return detailed_inv


#
# Hey, doc: we're in a module!
#
if (__name__ == '__main__'):
    print('Module => Do not execute')
