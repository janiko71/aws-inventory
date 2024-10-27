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
    write_log(message)
    get_all_regions()
    test_region_connectivity(region)
    transform_function_name(func_name)
    json_serial(obj)
    create_services_structure(policy_file)
    list_used_services(policy_file)
"""

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
json_file_path = os.path.join(output_dir, f"inventory_result_{timestamp}.json")

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

# Determine the number of CPU cores
num_cores = multiprocessing.cpu_count()

# Set the number of threads to 2 to 4 times the number of CPU cores
num_threads = num_cores * 4  # You can adjust this multiplier based on your needs

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
        global results, boto3_clients, successful_services, failed_services
        write_log(f"Starting inventory for {self.service} in {self.region} using {self.func}")
        try:
            client_key = (self.service, self.region)
            if client_key not in boto3_clients:
                boto3_clients[client_key] = boto3.client(self.service.lower(), region_name=self.region)
            client = boto3_clients[client_key]
            
            # First sub-task: API call
            start_time = time.time()
            inventory = client.__getattribute__(self.func)()
            self.progress_callback(1)  # Update progress bar by 1 task
            end_time = time.time()
            write_log(f"API call for {self.service} in {self.region} took {end_time - start_time:.2f} seconds")
            
            if not with_meta:
                inventory.pop('ResponseMetadata', None)
            object_type = list(inventory.keys())[0] if inventory else 'Unknown'
            if self.category not in results:
                results[self.category] = {}
            if self.service not in results[self.category]:
                results[self.category][self.service] = {}
            if object_type not in results[self.category][self.service]:
                results[self.category][self.service][object_type] = {}
            if self.region not in results[self.category][self.service][object_type]:
                results[self.category][self.service][object_type][self.region] = {}
            
            # Second sub-task: Processing results
            start_time = time.time()
            results[self.category][self.service][object_type][self.region] = inventory
            self.progress_callback(1)  # Update progress bar by 1 task
            end_time = time.time()
            write_log(f"Processing results for {self.service} in {self.region} took {end_time - start_time:.2f} seconds")
            successful_services += 1  # Increment successful services counter

        except botocore.exceptions.ClientError as e1:
            write_log(f"Error (1) querying {self.service} in {self.region} using {self.func}: {e1} ({type(e1)})")
            failed_services += 1  # Increment failed services counter
            self.progress_callback(2)  # Update progress bar by 2 tasks for failed service
        except Exception as e2:
            write_log(f"Error (2) querying {self.service} in {self.region} using {self.func}: {e2} ({type(e2)})")
            failed_services += 1  # Increment failed services counter
            self.progress_callback(2)  # Update progress bar by 2 tasks for failed service
        finally:
            write_log(f"Completed inventory for {self.service} in {self.region} using {self.func}")

def write_log(message):
    """
    Write a log message to the log file.

    Args:
        message (str): The message to log.
    """
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def get_all_regions():
    """
    Retrieve all AWS regions.

    Returns:
        list: A list of all AWS regions.
    """
    ec2 = boto3.client('ec2')
    response = ec2.describe_regions()
    return response['Regions']

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
        write_log(f"Could not connect to the endpoint URL for region {region}: {e}")
        return False

def transform_function_name(func_name):
    """
    Transform a CamelCase function name to snake_case.

    Args:
        func_name (str): The CamelCase function name.

    Returns:
        str: The snake_case function name.
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', func_name).lower()

def json_serial(obj):
    """
    JSON serializer for objects not serializable by default.

    Args:
        obj (any): The object to serialize.

    Returns:
        str: The serialized object.

    Raises:
        TypeError: If the object is not serializable.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")

def create_services_structure(policy_file):
    """
    Create a structure of services based on the provided IAM policy file.

    Args:
        policy_file (str): The path to the IAM policy file.

    Returns:
        dict: A dictionary structure of services.
    """
    service_to_category = {
        'ec2': 'Compute',
        'ecs': 'Compute',
        'eks': 'Compute',
        'lambda': 'Compute',
        'lightsail': 'Compute',
        's3': 'Storage',
        'ebs': 'Storage',
        'efs': 'Storage',
        'rds': 'Databases',
        'dynamodb': 'Databases',
        'redshift': 'Databases',
        'elasticache': 'Databases',
        'vpc': 'Networking',
        'elb': 'Networking',
        'cloudfront': 'Networking',
        'route53': 'Networking',
        'apigateway': 'Networking',
        'cloudwatch': 'Monitoring and Management',
        'cloudtrail': 'Monitoring and Management',
        'config': 'Monitoring and Management',
        'iam': 'IAM and Security',
        'kms': 'IAM and Security',
        'secretsmanager': 'IAM and Security',
        'waf': 'IAM and Security',
        'shield': 'IAM and Security',
        'sagemaker': 'Machine Learning',
        'rekognition': 'Machine Learning',
        'comprehend': 'Machine Learning',
        'glue': 'Analytics',
        'sns': 'Application Integration',
        'sqs': 'Application Integration',
        'stepfunctions': 'Application Integration',
        'cloudformation': 'Management & Governance'
    }

    with open(policy_file, 'r') as file:
        policy = json.load(file)

    services = {}
    for statement in policy.get('Statement', []):
        for action in statement.get('Action', []):
            service_prefix, action_name = action.split(':')
            if service_prefix in service_to_category:
                category = service_to_category[service_prefix]
                if category not in services:
                    services[category] = {}
                if service_prefix not in services[category]:
                    services[category][service_prefix] = []
                transformed_action_name = transform_function_name(action_name)
                if transformed_action_name not in services[category][service_prefix]:
                    services[category][service_prefix].append(transformed_action_name)

    return services

def list_used_services(policy_file):
    """
    List used services based on the provided IAM policy file.

    Args:
        policy_file (str): The path to the IAM policy file.

    Returns:
        dict: A dictionary of the used services.
    """
    global results, total_tasks, progress_bar, successful_services, failed_services

    start_time = time.time()
    
    regions = get_all_regions()

    if not regions:
        write_log("Unable to retrieve the list of regions.")
        return

    services = create_services_structure(policy_file)
    thread_list = []

    def progress_callback(amount):
        """Callback function to update the progress bar."""
        progress_bar.update(amount)

    for region in regions:
        region_name = region['RegionName']
        if test_region_connectivity(region_name):
            for category, service_dict in services.items():
                for service, func_list in service_dict.items():
                    for func in func_list:
                        write_log(f"Querying region: {region_name}, service: {service}, function: {func}")
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

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"\nTotal execution time: {execution_time:.2f} seconds")
    print(f"Total services called: {total_tasks // 2}")  # Divide by 2 to get the actual number of services called
    print(f"Successful services: {successful_services}")
    print(f"Failed services: {failed_services}")
    
    with open(json_file_path, "w") as json_file:
        json.dump(results, json_file, indent=4, default=json_serial)

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='AWS Inventory Script')
    parser.add_argument('--policy-file', type=str, default='inventory_policy_1.json', help='The path to the IAM policy file')
    parser.add_argument('--with-meta', action='store_true', help='Include metadata in the inventory')
    args = parser.parse_args()

    policy_file = args.policy_file
    with_meta = args.with_meta

    services_data = list_used_services(policy_file)