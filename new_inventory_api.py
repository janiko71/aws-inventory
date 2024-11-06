# NEW_INVENTORY_API.PY CONTEXT
"""
AWS Inventory Script

This script inventories AWS services used for a given account across all available regions.
It uses multithreading to perform inventory operations concurrently.

Modules:
    threading
    botocore
    boto3
    json
    os
    sys
    re
    datetime
    time
    argparse
    multiprocessing
    concurrent.futures
    tqdm

Classes:
    InventoryThread

Functions:
    # Utility Functions
    write_log(message)
    transform_function_name(func_name)
    json_serial(obj)
    is_empty(value)

    # Inventory Management Functions
    get_all_regions()
    test_region_connectivity(region)
    create_services_structure(policy_files)
    inventory_handling(category, region, service, func, progress_callback)
    list_used_services(policy_files)

    # Main Function
    main()
"""

import pprint
import threading
import boto3
import botocore
import json
import os
import sys
from datetime import datetime
import time
import argparse
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import glob
from utils import write_log, transform_function_name, json_serial, is_empty  # Importer les fonctions utilitaires
from botocore.exceptions import EndpointConnectionError, ClientError # Ajout des exceptions

# Ensure log directory exists
log_dir = "log"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Ensure output directory exists
output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Create a timestamped log file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file_path = os.path.join(log_dir, f"log_{timestamp}.log")

# Global variables
boto3_clients = {}  # Dictionary to store boto3 clients for different services and regions
results = {}  # Dictionary to store the inventory results
account_id = None  # AWS account ID

# Progress counters
total_tasks = 0  # Counter for the total number of tasks
completed_tasks = 0  # Counter for the number of completed tasks
progress_bar = None  # Progress bar object

# Service response counters
successful_services = 0  # Counter for the number of successful service responses
failed_services = 0  # Counter for the number of failed service responses
skipped_services = 0  # Counter for skipped services
empty_services = 0
filled_services = 0

# Determine the number of CPU cores
num_cores = multiprocessing.cpu_count()

# Set the number of threads to 2 to 4 times the number of CPU cores
num_threads = num_cores * 4  # You can adjust this multiplier based on your needs
# num_threads = 1 # For test purposes

# ------------------------------------------------------------------------------

# Multithreading Class

class InventoryThread(threading.Thread):
    """Thread class for performing inventory tasks."""

    def __init__(self, category, region, service, func, key, progress_callback):
        """
        Initialize the InventoryThread.

        Args:
            category (str): The category of the service.
            region (str): The AWS region.
            service (str): The AWS service.
            func (str): The function to call on the service.
            key (str): A unique key for the task.
            progress_callback (function): A callback function to update the progress bar.
        """
        threading.Thread.__init__(self)
        self.category = category
        self.region = region
        self.service = service
        self.func = func
        self.key = key
        self.progress_callback = progress_callback

    def run(self):
        """Run the inventory task."""
        inventory_handling(self.category, self.region, self.service, self.func, self.progress_callback)

# ------------------------------------------------------------------------------

# Inventory Management Functions

def get_all_regions():

    """
    Retrieve all AWS regions.

    Returns:
        list: A list of all AWS regions.
    """

    ec2 = boto3.client('ec2')
    response = ec2.describe_regions()

    return response['Regions']

# ------------------------------------------------------------------------------

def test_region_connectivity(region):

    """
    Test connectivity to a specific AWS region.

    Args:
        region (str): The AWS region to test.

    Returns:
        bool: True if the region is reachable, False otherwise.
    """

    ec2 = boto3.client('ec2', region_name=region)

    try:
        ec2.describe_availability_zones()
        return True
    except Exception as e:
        write_log(f"Could not connect to the endpoint URL for region {region}: {e}", log_file_path)
        return False

# ------------------------------------------------------------------------------

def create_services_structure(policy_files):

    """
    Create a structure of services based on the provided IAM policy files. In the JSON file 'service_structure.json', all inventoried resources are categorized.

    Args:
        policy_files (list): A list of paths to the IAM policy files.

    Returns:
        dict: A dictionary structure of services.
    """

    with open('service_structure.json', 'r') as file:
        service_to_category = json.load(file)

    services = {'global': {}, 'regional': {}}  # Add keys for global and regional services

    for policy_file in policy_files:

        # We read each policy file

        with open(policy_file, 'r') as file:

            policy = json.load(file)

            for statement in policy.get('Statement', []):
                
                for action in statement.get('Action', []):

                    service_prefix, action_name = action.split(':')
                    category = service_to_category.get(service_prefix, 'Unknown')

                    if policy_file.endswith('inventory_policy_global.json'):

                        # Global policy: 

                        if service_prefix not in services['global']:
                            services['global'][service_prefix] = []

                        transformed_action_name = transform_function_name(action_name)
                        services['global'][service_prefix].append(transformed_action_name)

                    else:

                        # Regional policy: 

                        if category not in services['regional']:
                            services['regional'][category] = {}
                        if service_prefix not in services['regional'][category]:
                            services['regional'][category][service_prefix] = []
                        transformed_action_name = transform_function_name(action_name)
                        if transformed_action_name not in services['regional'][category][service_prefix]:
                            services['regional'][category][service_prefix].append(transformed_action_name)

    return services

# ------------------------------------------------------------------------------

def inventory_handling(category, region, service, func, progress_callback):

    """
    This is the 'heart' of the script. Handles the inventory retrieval and processing for a specified AWS service and region.

    Args:
        category (str): The category of the inventory items.
        region (str): The AWS region to query.
        service (str): The AWS service to query.
        func (str): The function name to call on the client to retrieve the inventory.
        progress_callback (function): A callback function to report progress.
        None: The function updates global variables with the inventory results.

    Raises:
        AttributeError: If the specified function does not exist on the client.
        botocore.exceptions.ClientError: If there is an error making the API call.
        EndpointConnectionError: If there is a connection error to the endpoint.
        Exception: For any other exceptions that occur during processing.
    """

    # --- Factorization. This code is used twice but only in 'inventory_handling'

    def detail_handling(client, inventory, extra_call_config, sub_config, result_key, item_key, item_search_id):

        """
        Handles the detailed retrieval and updating of inventory items using a specified client and configuration.

        Args:
            client (object): The client object used to make API calls.
            inventory (dict): The inventory data containing items to be processed.
            extra_call_config (dict): Additional configuration for the API call, including complementary parameters.
            sub_config (dict): Sub-configuration containing details about the function and parameters for the API call.
            result_key (str): The key in the API response that contains the detailed information.
            item_key (str): The key in the inventory dictionary that contains the list of items to be processed.
            item_search_id (str): The key in each item used to search for detailed information.

        Returns:
            None: The function updates the inventory items in place with the detailed information retrieved from the API.
        """

        items = inventory.get(item_key, [])

        for item in items:

            if type(item) not in [dict, list]:
                item = {item}

            detail_param_value = item[item_search_id]
            detail_function = sub_config['detail_function']
            detail_param = sub_config['detail_param']
            complementary_params = extra_call_config.get('complementary_param', None)

            # exception for s3 location: we need an additionnal arg (account id)

            if service == 's3' and detail_function == 'get_bucket_location':
                if not complementary_params:
                    complementary_params = {'ExpectedBucketOwner': account_id}
                else:
                    complementary_params.update({'ExpectedBucketOwner': account_id})

            # General case

            detail_response = {}

            # Calling all the corresponding detail services (see 'extra_service_call.json')

            try:
                if complementary_params:
                    detail_response = client.__getattribute__(detail_function)(**{detail_param: detail_param_value, **complementary_params})
                else:
                    detail_response = client.__getattribute__(detail_function)(**{detail_param: detail_param_value})
                if not with_meta:
                    detail_response.pop('ResponseMetadata', None)
            except botocore.exceptions.ClientError as e1:
                exception_function_name = transform_function_name(e1.operation_name)
                if exception_function_name != detail_function:
                    raise e1

            # The response is sometimes empty, sometimes a string, sometimes a list or a dict

            if len(detail_response) > 0:
                if type(detail_response) not in [dict, list]:
                    detail_response = {result_key: detail_response[result_key]}
                item.update(detail_response)
            else:
                if result_key != "":
                    item.update({result_key: {}})

    # --- Main body of the 'inventory_handling' function

    global account_id, results, successful_services, failed_services, skipped_services, empty_services, filled_services
    
    write_log(f"Starting inventory for {service} in {region} using {func}", log_file_path)

    try:

        # --- Some exceptions for resources/services with names different from boto3 name, and some inventory for EC2 needs a region even when global (ex : DescribeRegions)

        if region != 'global':
            if service == 'states':
                client = boto3.client('stepfunctions', region_name=region)
            else:
                client = boto3.client(service.lower(), region_name=region)
        else:
            if service == 'ec2':
                client = boto3.client(service.lower(), region_name='us-east-1')
            else:
                client = boto3.client(service.lower())

        # --- Inventory call for the resource. Reminder: called through threading
        
        start_time = time.time()
        inventory = client.__getattribute__(func)()
        progress_callback(1)
        end_time = time.time()
        write_log(f"API call for {service} in {region} took {end_time - start_time:.2f} seconds", log_file_path)

        # --- Cmd line arg "with-meta" ('ResponseMetaData)

        if not with_meta:
            response_metadata = inventory.pop('ResponseMetadata', None)

        # --- Constructing the inventory
        
        empty_items = True # a result is considered as 'empty' if it has no interesting value ('NextToken' or 'ResponseMetada' have no intersting value for an inventory)

        for key, value in inventory.items():
            if not is_empty(value) and key not in {'NextToken'}:
                empty_items = False
                break

        if not empty_items or with_empty:
            
            # --- Here: not empty, or we want to list the empty values too (arg 'with_empty')

            object_type = list(inventory.keys())[0] if inventory else 'Unknown'
            if category not in results:
                results[category] = {}
            if service not in results[category]:
                results[category][service] = {}
            if object_type not in results[category][service]:
                results[category][service][object_type] = {}
            if region not in results[category][service][object_type]:
                results[category][service][object_type][region] = {}

            start_time = time.time()

            inventory.pop('NextToken', None) # no "NextToken"
            results[category][service][object_type][region] = inventory
            if with_meta and response_metadata:
                # MetaData only if the key is present and if we asked for it (arg 'with_meta')
                results[category][service][object_type][region]['ResponseMetadata'] = response_metadata

            end_time = time.time()
            write_log(f"Processing results for {service} in {region} took {end_time - start_time:.2f} seconds", log_file_path)
            filled_services += 1

            # --- In case of: we want more information about the resource
            #     Calling all the corresponding detail services (see 'extra_service_call.json')

            if service in extra_service_calls:

                extra_call_config = extra_service_calls[service]
                
                # -- Testing extra_call_config: singleton or multiple key/value items ?

                if all(isinstance(value, dict) for value in extra_call_config.values()):

                    # Multiple key/value items

                    for sub_key, sub_config in extra_call_config.items():
                        result_key = sub_config['result_key']
                        item_key = sub_config['item_key']
                        item_search_id = sub_config['item_search_id']

                        detail_handling(client, inventory, extra_call_config, sub_config, result_key, item_key, item_search_id)

                else:

                    # Single key/value                    
                    result_key = extra_call_config['result_key']
                    item_key = extra_call_config['item_key']
                    item_search_id = extra_call_config['item_search_id']

                    detail_handling(client, inventory, extra_call_config, sub_config, result_key, item_key, item_search_id)

        else:

            # The inventory is empty, but don't forget to count (for the progression bar)
            empty_services += 1
            write_log(f"Empty results for {service} in {region}", log_file_path)

        # Inventory successfull

        progress_callback(1)
        successful_services += 1

    except AttributeError as e1:

        write_log(f"Error (1) querying {service} in {region} using {func}: {e1} ({type(e1)})", log_file_path)
        failed_services += 1
        progress_callback(2)

    except botocore.exceptions.ClientError as e2: 

        if type(e2).__name__ == 'AWSOrganizationsNotInUseException':
            write_log(f"Warning (2): Skipping {service} in {region} due to organizations not in use error: {e2} ({type(e2)})", log_file_path)
            skipped_services += 1
            progress_callback(2)

        else:

            write_log(f"Error (3) querying {service} in {region} using {func}: {e2} ({type(e2)})", log_file_path)
            failed_services += 1
            progress_callback(2)

    except EndpointConnectionError as e3:

        write_log(f"Warning (4): Skipping {service} in {region} due to connection error: {e3} ({type(e3)})", log_file_path)
        skipped_services += 1
        progress_callback(2)

    except Exception as e:

        write_log(f"Error (e) querying {service} in {region} using {func}: {e} ({type(e)})", log_file_path)
        failed_services += 1
        progress_callback(2)

    finally:

        write_log(f"Completed inventory for {service} in {region} using {func}", log_file_path)



        
# ------------------------------------------------------------------------------

def list_used_services(policy_files):
    """
    List used services based on the provided IAM policy files.

    This function performs the following steps:
    1. Retrieves all AWS regions.
    2. Creates a structure of services based on the provided IAM policy files.
    3. Initializes and manages threads to query both global and regional services.
    4. Updates a progress bar to reflect the progress of the inventory process.
    5. Logs the execution time and results of the inventory process.
    6. Writes the results to a JSON file.

    Args:
        policy_files (list): A list of paths to the IAM policy files.

    Returns:
        dict: A dictionary of the used services.
    """
    global account_id, results, total_tasks, progress_bar, successful_services, failed_services, filled_services, empty_services

    start_time = time.time()
    
    regions = get_all_regions()

    if not regions:
        write_log("Unable to retrieve the list of regions.", log_file_path)
        return

    services = create_services_structure(policy_files)
    thread_list = []

    def progress_callback(amount):
        """Callback function to update the progress bar."""
        progress_bar.update(amount)

    # Retrieve the AWS account ID using STS
    sts_client = boto3.client('sts')
    account_id = sts_client.get_caller_identity()["Account"]

    # Modify the JSON file path to include the account ID
    json_file_path = os.path.join(output_dir, f"inventory_{account_id}_{timestamp}.json")

    # Handle global services
    if 'global' in services:
        for service, func_list in services['global'].items():
            for func in func_list:
                write_log(f"Querying global service: {service}, function: {func}", log_file_path)
                total_tasks += 2  # Increment total_tasks for each sub-task

                thread = InventoryThread('global', 'global', service, func, f"{service} (global)", progress_callback)
                thread_list.append(thread)

    # Handle regional services
    for region in regions:
        region_name = region['RegionName']
        if test_region_connectivity(region_name):
            for category, service_dict in services['regional'].items():
                for service, func_list in service_dict.items():
                    for func in func_list:
                        write_log(f"Querying region: {region_name}, service: {service}, function: {func}", log_file_path)
                        total_tasks += 2  # Increment total_tasks for each sub-task
                        thread = InventoryThread(category, region_name, service, func, f"{service} in {region_name}", progress_callback)
                        thread_list.append(thread)

    # Initialize progress bar with the total number of sub-tasks
    progress_bar = tqdm(total=total_tasks, desc="Inventory Progress", unit="sub-task")

    # Use ThreadPoolExecutor to manage the threads
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        for thread in thread_list:
            executor.submit(thread.run)

    progress_bar.close()

   # Include the list of regions if --with-extra is specified
    if with_extra:
        results['regions'] = regions

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"\nTotal execution time: {execution_time:.2f} seconds")
    print(f"Total services called: {total_tasks // 2}")  # Divide by 2 to get the actual number of services called
    print(f"Successful services: {successful_services} ({filled_services} services with datas, {empty_services} empty services)")
    print(f"Failed services: {failed_services}")
    print(f"Skipped services: {skipped_services}")
    
    with open(json_file_path, "w") as json_file:
        json.dump(results, json_file, indent=4, default=json_serial)

    return results


# ------------------------------------------------------------------------------

# Main Function

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AWS Inventory Script')
    parser.add_argument('--policy-dir', type=str, default='policies', help='The directory containing the IAM policy files')
    parser.add_argument('--with-meta', action='store_true', help='Include metadata in the inventory')
    parser.add_argument('--with-extra', action='store_true', help='Include Availability Zones, Regions and Account Attributes in the inventory')
    parser.add_argument('--with-empty', action='store_true', help='Include empty values in the inventory')
    args = parser.parse_args()

    policy_dir = args.policy_dir
    with_meta = args.with_meta
    with_extra = args.with_extra
    with_empty = args.with_empty

    # Find all policy files matching the pattern inventory_policy_local_X.json
    policy_files = glob.glob(os.path.join(policy_dir, 'inventory_policy_local_*.json'))

    # Add the global policy file
    global_policy_file = os.path.join(policy_dir, 'inventory_policy_global.json')
    if os.path.exists(global_policy_file):
        policy_files.append(global_policy_file)

    # Load extra service calls configuration
    extra_service_file = os.path.join(policy_dir, 'extra_service_calls.json')
    with open(extra_service_file, 'r') as file:
        extra_service_calls = json.load(file)
        # Process extra service calls configuration
        for service, config in extra_service_calls.items():
            if ':' in service:
                _, list_function = service.split(':')
                extra_service_calls[service]['list_function'] = list_function

    if not policy_files:
        print("No policy files found.")
        sys.exit(1)

    services_data = list_used_services(policy_files)