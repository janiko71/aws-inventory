# NEW_INVENTORY_API.PY CONTEXT
"""
AWS Inventory Script

This script inventories AWS resources used for a given account across all available regions.
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
    create_resources_structure(inventory_structure)
    inventory_handling(category, region, resource, func, progress_callback)
    list_used_resources(inventory_structure)

    # Main Function
    main()
"""

import threading
import boto3
import json
import yaml
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
from botocore.exceptions import EndpointConnectionError, ClientError  # Ajout des exceptions

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
boto3_clients = {}  # Dictionary to store boto3 clients for different resources and regions
results = {}  # Dictionary to store the inventory results
account_id = None  # AWS account ID

# Progress counters
total_tasks = 0  # Counter for the total number of tasks
completed_tasks = 0  # Counter for the number of completed tasks
progress_bar = None  # Progress bar object

# resource response counters
successful_resources = 0  # Counter for the number of successful resource responses
failed_resources = 0  # Counter for the number of failed resource responses
skipped_resources = 0  # Counter for skipped resources
empty_resources = 0
filled_resources = 0

# Determine the number of CPU cores
num_cores = multiprocessing.cpu_count()

# Set the number of threads to 2 to 4 times the number of CPU cores
num_threads = num_cores * 4  # You can adjust this multiplier based on your needs
# num_threads = 1 # For test purposes

# ------------------------------------------------------------------------------

# Multithreading Class

class InventoryThread(threading.Thread):

    """Thread class for performing inventory tasks."""

    def __init__(self, category, region, resource, func, key, inventory_nodes, progress_callback):
        """
        Initialize the InventoryThread.

        Args:
            category (str): The category of the resource.
            region (str): The AWS region.
            resource (str): The AWS resource.
            func (str): The function to call on the resource.
            key (str): A unique key for the task.
            progress_callback (function): A callback function to update the progress bar.
        """
        threading.Thread.__init__(self)
        self.category = category
        self.region = region
        self.resource = resource
        self.func = func
        self.key = key
        self.inventory_nodes = inventory_nodes
        self.progress_callback = progress_callback

    def run(self):
        """Run the inventory task."""
        inventory_handling(self.category, self.region, self.resource, self.func, self.inventory_nodes, self.progress_callback)

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

def inventory_handling(category, region, resource, func, inventory_nodes, progress_callback):

    """
    This is the 'heart' of the script. Handles the inventory retrieval and processing for a specified AWS resource and region.

    Args:
        category (str): The category of the inventory items.
        region (str): The AWS region to query.
        resource (str): The AWS resource to query.
        func (str): The function name to call on the client to retrieve the inventory.
        inventory_nodes (list): A list of inventory nodes to retrieve additional information.
        progress_callback (function): A callback function to report progress.
        None: The function updates global variables with the inventory results.

    Raises:
        AttributeError: If the specified function does not exist on the client.
        botocore.exceptions.ClientError: If there is an error making the API call.
        EndpointConnectionError: If there is a connection error to the endpoint.
        Exception: For any other exceptions that occur during processing.
    """

    # --- Factorization. This code is used twice but only in 'inventory_handling'

    def detail_handling(client, inventory, detail_function, inventory_node):

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

        global account_id

        items = inventory.get(inventory_node['item_key'], [])

        for item in items:

            if type(item) not in [dict, list]:
                item = {item}

            for detail in inventory_node['details']:

                node = inventory_node['details'][detail]

                item_search_id = node['item_search_id']
                detail_function = node['detail_function']
                detail_param = node['detail_param']   
                complementary_params = node.get('complementary_param', None)

                detail_param_value = item[item_search_id]

                # exception for s3 location: we need an additionnal arg (account id)

                if resource == 's3' and detail_function == 'get_bucket_location':
                    if not complementary_params:
                        complementary_params = {'ExpectedBucketOwner': account_id}
                    else:
                        complementary_params.update({'ExpectedBucketOwner': account_id})

                # General case

                detail_response = {}

                # Calling all the corresponding detail resources (see 'extra_resource_call.json')

                try:
                    if complementary_params:
                        detail_response = client.__getattribute__(detail_function)(**{detail_param: detail_param_value, **complementary_params})
                    else:
                        detail_response = client.__getattribute__(detail_function)(**{detail_param: detail_param_value})
                    if not with_meta:
                        detail_response.pop('ResponseMetadata', None)
                except ClientError as e1:
                    exception_function_name = transform_function_name(e1.operation_name)
                    if exception_function_name != detail_function:
                        raise e1

                # The response is sometimes empty, sometimes a string, sometimes a list or a dict

                if len(detail_response) > 0:
                    if type(detail_response) not in [dict, list]:
                        detail_response = {detail: detail_response[detail]}
                    item.update(detail_response)
                else:
                    if detail != "":
                        item.update({detail: {}})

    # --- Main body of the 'inventory_handling' function

    global account_id, results, successful_resources, failed_resources, skipped_resources, empty_resources, filled_resources

    write_log(f"Starting inventory for {resource} in {region} using {func}", log_file_path)

    try:

        # --- Some exceptions for resources/services with names different from boto3 name, and some inventory for EC2 needs a region even when global (ex : DescribeRegions)

        if region != 'global':
            if resource == 'states':
                client = boto3.client('stepfunctions', region_name=region)
            elif resource == 'private-networks':
                client = boto3.client("privatenetworks", region_name=region)
            elif resource == 'elasticfilesystem':
                client = boto3.client("efs", region_name=region)
            elif resource == 'neptune-db':
                client = boto3.client("neptunedata", region_name=region)
            else:
                client = boto3.client(resource.lower(), region_name=region)
        else:
            if resource == 'ec2':
                client = boto3.client(resource.lower(), region_name='us-east-1')
            else:
                client = boto3.client(resource.lower())

        # --- Inventory call for the resource. Reminder: called through threading

        start_time = time.time()
        inventory = client.__getattribute__(func)()
        progress_callback(1)
        end_time = time.time()
        write_log(f"API call for {resource} in {region} took {end_time - start_time:.2f} seconds", log_file_path)

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
            if resource not in results[category]:
                results[category][resource] = {}
            if object_type not in results[category][resource]:
                results[category][resource][object_type] = {}
            if region not in results[category][resource][object_type]:
                results[category][resource][object_type][region] = {}

            start_time = time.time()

            inventory.pop('NextToken', None) # no "NextToken"
            results[category][resource][object_type][region] = inventory
            if with_meta and response_metadata:
                # MetaData only if the key is present and if we asked for it (arg 'with_meta')
                results[category][resource][object_type][region]['ResponseMetadata'] = response_metadata

            end_time = time.time()
            write_log(f"Processing results for {resource} in {region} took {end_time - start_time:.2f} seconds", log_file_path)
            filled_resources += 1

            # --- In case of: we want more information about the resource
            #     Calling all the corresponding detail resources 

            for detail_function in inventory_nodes:

                 detail_handling(client, inventory, detail_function, inventory_nodes[detail_function])

        else:

            # The inventory is empty, but don't forget to count (for the progression bar)
            empty_resources += 1
            write_log(f"Empty results for {resource} in {region}", log_file_path)

        # Inventory successfull

        progress_callback(1)
        successful_resources += 1

    except AttributeError as e1:

        write_log(f"Error (1) querying {resource} in {region} using {func}: {e1} ({type(e1)})", log_file_path)
        failed_resources += 1
        progress_callback(2)

    except ClientError as e2:

        if type(e2).__name__ == 'AWSOrganizationsNotInUseException':

            write_log(f"Warning (2): Skipping {resource} in {region} due to organizations not in use error: {e2} ({type(e2)})", log_file_path)
            skipped_resources += 1
            progress_callback(2)

        else:

            write_log(f"Error (3) querying {resource} in {region} using {func}: {e2} ({type(e2)})", log_file_path)
            failed_resources += 1
            progress_callback(2)

    except EndpointConnectionError as e3:

        write_log(f"Warning (4): Skipping {resource} in {region} due to connection error: {e3} ({type(e3)})", log_file_path)
        skipped_resources += 1
        progress_callback(2)

    except Exception as e:

        write_log(f"Error (e) querying {resource} in {region} using {func}: {e} ({type(e)})", log_file_path)
        failed_resources += 1
        progress_callback(2)

    finally:

        write_log(f"Completed inventory for {resource} in {region} using {func}", log_file_path)


# ------------------------------------------------------------------------------

def list_used_resources(inventory_structure):

    """
    List used resources based on the provided YAML files.

    This function performs the following steps:
    1. Retrieves all AWS regions.
    2. Creates a structure of resources based on the provided IAM policy files.
    3. Initializes and manages threads to query both global and regional resources.
    4. Updates a progress bar to reflect the progress of the inventory process.
    5. Logs the execution time and results of the inventory process.
    6. Writes the results to a JSON file.

    Args:
        inventory_structure (list): A structure of resources based on the provided YAML file with all informations about the resources.

    Returns:
        dict: A dictionary of the used resources.
    """

    # ------------------------------------------------------------------------------

    def progress_callback(amount):
        
        """
        Callback function to update the progress bar.

        Args:
            amount (int): The amount by which to update the progress bar.
        """

        progress_bar.update(amount)

    # ------------------------------------------------------------------------------

    def resource_inventory(progress_callback, thread_list, category, resource, functions, inventory_nodes, region):


        """
        Collects resource inventory for a specified AWS resource and region, and updates progress.
        Args:
            progress_callback (function): A callback function to update progress.
            thread_list (list): A list to store threads for concurrent execution.
            category (str): The category of the AWS resource.
            resource (str): The AWS resource to query.
            functions (list): A list of functions to execute for the resource.
            inventory_nodes (list): A list to store inventory nodes.
            region (dict): A dictionary containing region information, with 'RegionName' as a key.
        Returns:
            None
        """

        global total_tasks

        for func in functions:
            
            write_log(f"Querying category: {category}, resource: {resource}, function: {func}, region: {region['RegionName']}", log_file_path)
            total_tasks += 2  # Increment total_tasks for each sub-task
            thread = InventoryThread(category, region['RegionName'], resource, func, f"{resource} in {region['RegionName']}", inventory_nodes, progress_callback)
            thread_list.append(thread)

    # ------------------------------------------------------------------------------

    global account_id, results, total_tasks, progress_bar, successful_resources, failed_resources, filled_resources, empty_resources

    start_time = time.time()

    # --- Get AWS regions

    regions = get_all_regions()

    if not regions:
        write_log("Unable to retrieve the list of regions.", log_file_path)
        return

    thread_list = []

    # --- Retrieve the AWS account ID using STS

    sts_client = boto3.client('sts')
    account_id = sts_client.get_caller_identity()["Account"]

    # --- Modify the JSON file path to include the account ID

    json_file_path = os.path.join(output_dir, f"inventory_{account_id}_{timestamp}.json")

    # --- Handle all resources

    for resource_info in inventory_structure:

        for resource in resource_info:

            inventory_info = resource_info[resource]

            category = inventory_info.get('category', 'unknown')
            functions = inventory_info.get('inventory_nodes', [])
            boto_resource_name = inventory_info.get('boto_resource_name', [])
            regions_type = inventory_info.get('region_type', ['local'])
            inventory_nodes = inventory_info.get('inventory_nodes', [])

            if 'global' in regions_type:

                # For global resources, we only need to query once
                resource_inventory(progress_callback, thread_list, category, boto_resource_name, functions, inventory_nodes, {'RegionName': 'global'})

            else:

                # For local resources, we need to query each region

                for region in regions:

                    if test_region_connectivity(region['RegionName']):
                        resource_inventory(progress_callback, thread_list, category, boto_resource_name, functions, inventory_nodes, region)

    # --- Initialize progress bar with the total number of sub-tasks

    progress_bar = tqdm(total=total_tasks, desc="Inventory Progress", unit="sub-task")

    # --- Use ThreadPoolExecutor to manage the threads

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        for thread in thread_list:
            executor.submit(thread.run)

    progress_bar.close()

    # --- Include the list of regions if --with-extra is specified

    if with_extra:
        results['regions'] = regions

    end_time = time.time()
    execution_time = end_time - start_time

    # --- Display summary of the inventory process

    print(f"\nTotal execution time: {execution_time:.2f} seconds")
    print(f"Total resources called: {total_tasks // 2}")  # Divide by 2 to get the actual number of resources called
    print(f"Successful resources: {successful_resources} ({filled_resources} resources with datas, {empty_resources} empty resources)")
    print(f"Failed resources: {failed_resources}")
    print(f"Skipped resources: {skipped_resources}")
    
    # --- Write the results to a JSON file

    with open(json_file_path, "w") as json_file:
        json.dump(results, json_file, indent=4, default=json_serial)

    return results


# ------------------------------------------------------------------------------

# Main Function

# ------------------------------------------------------------------------------

if __name__ == "__main__":

    # --- Handle command-line arguments

    parser = argparse.ArgumentParser(description='AWS Inventory Script')
    parser.add_argument('--resource-dir', type=str, default='resources', help='The directory containing the resource files containing the inventory resources')
    parser.add_argument('--with-meta', action='store_true', help='Include metadata in the inventory')
    parser.add_argument('--with-extra', action='store_true', help='Include Availability Zones, Regions and Account Attributes in the inventory')
    parser.add_argument('--with-empty', action='store_true', help='Include empty values in the inventory')
    args = parser.parse_args()

    resource_dir = args.resource_dir
    with_meta = args.with_meta
    with_extra = args.with_extra
    with_empty = args.with_empty

    # --- Find all policy files matching the pattern inventory_policy_local_X.json

    policy_files = glob.glob(os.path.join(resource_dir, 'inventory_policy_local_*.json'))

    # --- Find all YAML policy files in the policy directory

    yaml_policy_files = glob.glob(os.path.join(resource_dir, '*.yaml'))

    # --- Convert YAML policy files to JSON and keep this structure for later use

    inventory_structure = []
    for yaml_file in yaml_policy_files:
        with open(yaml_file, 'r') as file:
            yaml_content = yaml.safe_load(file)
            inventory_structure.append(yaml_content)

    if not inventory_structure:
        print("No resource files found.")
        sys.exit(1)

    # --- Perform inventory and list used resources

    resources_data = list_used_resources(inventory_structure)

    # That's all folks!