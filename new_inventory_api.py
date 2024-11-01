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
import re
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
    Create a structure of services based on the provided IAM policy files.

    Args:
        policy_files (list): A list of paths to the IAM policy files.

    Returns:
        dict: A dictionary structure of services.
    """
    with open('service_structure.json', 'r') as file:
        service_to_category = json.load(file)

    services = {'global': {}, 'regional': {}}  # Add keys for global and regional services
    for policy_file in policy_files:
        with open(policy_file, 'r') as file:
            policy = json.load(file)
            for statement in policy.get('Statement', []):
                for action in statement.get('Action', []):
                    service_prefix, action_name = action.split(':')
                    if service_prefix in service_to_category:
                        category = service_to_category[service_prefix]
                        if policy_file.endswith('inventory_policy_global.json'):
                            if service_prefix not in services['global']:
                                services['global'][service_prefix] = []
                            transformed_action_name = transform_function_name(action_name)
                            if transformed_action_name not in services['global'][service_prefix]:
                                services['global'][service_prefix].append(transformed_action_name)
                        else:
                            if category not in services['regional']:
                                services['regional'][category] = {}
                            if service_prefix not in services['regional'][category]:
                                services['regional'][category][service_prefix] = []
                            transformed_action_name = transform_function_name(action_name)
                            if transformed_action_name not in services['regional'][category][service_prefix]:
                                services['regional'][category][service_prefix].append(transformed_action_name)

    #pprint.pprint(services)
    return services

# ------------------------------------------------------------------------------

def inventory_handling(category, region, service, func, progress_callback):
    """
    Handle the inventory task for a given service and region.

    Args:
        category (str): The category of the service.
        region (str): The AWS region.
        service (str): The AWS service.
        func (str): The function to call on the service.
        progress_callback (function): A callback function to update the progress bar.

    Returns:
        None
    """
    global results, successful_services, failed_services, skipped_services, empty_services, filled_services
    if with_extra or func not in {'describe_availability_zones', 'describe_regions', 'describe_account_attributes'}:
        write_log(f"Starting inventory for {service} in {region} using {func}", log_file_path)
        try:
            if region != 'global':
                if service == 'states':
                    client = boto3.client('stepfunctions', region_name=region)
                elif service == 'private-networks':
                    client = boto3.client("privatenetworks", region_name=region)
                else:
                    client = boto3.client(service.lower(), region_name=region)
            else:
                # Special case for 's3' service in the global context: no region specified
                if service == 'ec2':
                    client = boto3.client(service.lower(), region_name='us-east-1')
                else:
                    client = boto3.client(service.lower())
            
            # First sub-task: API call
            start_time = time.time()
            inventory = client.__getattribute__(func)()
            progress_callback(1)  # Update progress bar by 1 task
            end_time = time.time()
            write_log(f"API call for {service} in {region} took {end_time - start_time:.2f} seconds", log_file_path)
            
            # Extracting ResponseMetadata
            response_metadata = inventory.pop('ResponseMetadata', None)
            
            object_type = list(inventory.keys())[0] if inventory else 'Unknown'
            if category not in results:
                results[category] = {}
            if service not in results[category]:
                results[category][service] = {}
            if object_type not in results[category][service]:
                results[category][service][object_type] = {}

            # Check if there are non-empty items in the inventory (excluding 'NextToken' because some services responds with an empty table but with a NextToken)
            empty_items = False # temporary test
            #empty_items = True
            #for key, value in inventory.items():
            #    if not is_empty(value) and key not in {'NextToken'}:
            #        empty_items = False
            #        break
            # Check if there are non-empty items in the inventory excluding 'ResponseMetadata' and 'NextToken'
            # non_empty_items = next((v for k, v in inventory.items() if k != 'ResponseMetadata' and not is_empty(v) and not (len(v) == 1 and 'NextToken' in v)), None)
            if not empty_items or with_empty:
                if region not in results[category][service][object_type]:
                    results[category][service][object_type][region] = {}

                # Second sub-task: Processing results
                start_time = time.time()
                results[category][service][object_type][region] = inventory
                if with_meta:
                    results[category][service][object_type][region]['ResponseMetadata'] = response_metadata
                end_time = time.time()
                write_log(f"Processing results for {service} in {region} took {end_time - start_time:.2f} seconds", log_file_path)
                filled_services += 1
            else:
                empty_services += 1
                write_log(f"Empty results for {service} in {region}", log_file_path)
            progress_callback(1)  # Update progress bar by 1 task
            successful_services += 1  # Increment successful services counter

        except AttributeError as e1:
            write_log(f"Error (1) querying {service} in {region} using {func}: {e1} ({type(e1)})", log_file_path)
            failed_services += 1  # Increment failed services counter
            progress_callback(2)  # Update progress bar by 2 tasks for failed service
        except botocore.exceptions.ClientError as e2: 
            if type(e2).__name__ == 'AWSOrganizationsNotInUseException':
                write_log(f"Warning (2): querying {service} in {region} using {func}: error (organizations not in use): {e2} ({type(e2)})", log_file_path)
                skipped_services += 1  # Increment skipped services counter
                progress_callback(2)  # Update progress bar by 2 tasks for skipped service
            elif type(e2).__name__ == 'DirectConnectClientException':
                write_log(f"Warning (2): querying {service} in {region} using {func}: error (organizations not in use): {e2} ({type(e2)})", log_file_path)
                skipped_services += 1  # Increment skipped services counter
                progress_callback(2)  # Update progress bar by 2 tasks for skipped service
            else:
                write_log(f"Error (3) querying {service} in {region} using {func}: {e2} ({type(e2)})", log_file_path)
                failed_services += 1  # Increment failed services counter
                progress_callback(2)  # Update progress bar by 2 tasks for failed service
        except EndpointConnectionError as e3:
            write_log(f"Warning (4): querying {service} in {region} using {func}: error due to connection error: {e3} ({type(e3)})", log_file_path)
            skipped_services += 1  # Increment skipped services counter
            progress_callback(2)  # Update progress bar by 2 tasks for skipped service
        except Exception as e:
            write_log(f"Error (e) querying {service} in {region} using {func}: {e} ({type(e)})", log_file_path)
            failed_services += 1  # Increment failed services counter
            progress_callback(2)  # Update progress bar by 2 tasks for failed service
        finally:
            write_log(f"Completed inventory for {service} in {region} using {func}", log_file_path)

    else:
        skipped_services += 1  # Increment skipped services counter
        progress_callback(2)  # Update progress bar by 2 tasks for skipped service                
        write_log(f"Inventory for {service} in {region} using {func} skipped!", log_file_path)


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
    global results, total_tasks, progress_bar, successful_services, failed_services, filled_services, empty_services

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

    if not policy_files:
        print("No policy files found.")
        sys.exit(1)

    services_data = list_used_services(policy_files)