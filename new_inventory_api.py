"""
AWS Inventory Script

This script inventories AWS services used for a given account across all available regions.
It uses multithreading to perform inventory operations concurrently.

Modules:
    threading
    boto3
    json
    os
    sys
    datetime
    time
    concurrent.futures

Classes:
    AWSThread

Functions:
    write_log(message)
    get_all_regions()
    test_region_connectivity(region)
    list_ec2_instances(region)
    list_s3_buckets(region)
    create_services_structure(policy_file)
    list_used_services(policy_file)
"""

import threading
import boto3
import json
import os
import sys
import re
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor

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
boto3_clients = {}
results = {}

class InventoryThread(threading.Thread):
    """
    A thread class to handle inventory operations for a specific AWS service in a specific region.

    :param category: The category of the service (e.g., 'Compute')
    :type category: str
    :param region: The AWS region (e.g., 'us-west-1')
    :type region: str
    :param service: The AWS service (e.g., 'ec2')
    :type service: str
    :param func: The function to call on the boto3 client (e.g., 'describe_instances')
    :type func: str
    :param key: The key to use for logging and error messages
    :type key: str
    """
    def __init__(self, category, region, service, func, key):
        threading.Thread.__init__(self)
        self.category = category
        self.region = region
        self.service = service
        self.func = func
        self.key = key

    def run(self):
        """
        Run the inventory operation and log the results.
        """
        global results, boto3_clients
        write_log(f"Starting inventory for {self.service} in {self.region} using {self.func}")
        try:
            # Get or create boto3 client
            client_key = (self.service, self.region)
            if client_key not in boto3_clients:
                boto3_clients[client_key] = boto3.client(self.service.lower(), region_name=self.region)
            client = boto3_clients[client_key]
            
            # Call the function with the boto3 client
            inventory = client.__getattribute__(self.func)()
            
            # Extract the first key from the inventory to use as the object type
            object_type = list(inventory.keys())[0] if inventory else 'Unknown'
            
            # Ensure the category exists in the results
            if self.category not in results:
                results[self.category] = {}
            
            # Ensure the service exists within the category
            if self.service not in results[self.category]:
                results[self.category][self.service] = {}
            
            # Ensure the object type exists within the service
            if object_type not in results[self.category][self.service]:
                results[self.category][self.service][object_type] = {}
            
            # Ensure the region exists within the object type
            if self.region not in results[self.category][self.service][object_type]:
                results[self.category][self.service][object_type][self.region] = {}
            
            # Update the results with the inventory
            results[self.category][self.service][object_type][self.region] = inventory

        except Exception as e: 
            write_log(f"Error querying {self.service} in {self.region} using {self.func}: {e}")
        finally:
            write_log(f"Completed inventory for {self.service} in {self.region} using {self.func}")



def write_log(message):
    """
    Write a log message to the log file.

    :param message: The message to log
    :type message: str
    """
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def get_all_regions():
    """
    Retrieve the list of all AWS regions.

    :return: List of all AWS regions
    :rtype: list
    """
    ec2 = boto3.client('ec2')
    response = ec2.describe_regions()
    return response['Regions']

def test_region_connectivity(region):
    """
    Test connectivity to a given AWS region.

    :param region: The region to test
    :type region: str
    :return: True if connectivity is successful, False otherwise
    :rtype: bool
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
    Transform a camel case function name to snake case.

    :param func_name: The function name in camel case
    :type func_name: str
    :return: The function name in snake case
    :rtype: str
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', func_name).lower()
    
def create_services_structure(policy_file):
    """
    Create the services structure based on the IAM policy file.

    :param policy_file: The path to the IAM policy file
    :type policy_file: str
    :return: Dictionary of services categorized by type
    :rtype: dict
    """

    # Mapping of service prefixes to categories
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
    Inventory AWS services used for a given account across all available regions.

    :param policy_file: The path to the IAM policy file
    :type policy_file: str
    :return: Dictionary of services and their resources grouped by categories
    :rtype: dict
    """

    global results

    start_time = time.time()
    
    regions = get_all_regions()

    if not regions:
        write_log("Unable to retrieve the list of regions.")
        return

    services = create_services_structure(policy_file)
    thread_list = []

    for region in regions:
        region_name = region['RegionName']
        if test_region_connectivity(region_name):
            for category, service_dict in services.items():
                for service, func_list in service_dict.items():
                    for func in func_list:
                        write_log(f"Querying region: {region_name}, service: {service}, function: {func}")
                        thread = InventoryThread(category, region_name, service, func, f"{service} in {region_name}")
                        thread_list.append(thread)


    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"\nTotal execution time: {execution_time:.2f} seconds")
    
    with open(json_file_path, "w") as json_file:
        json.dump(results, json_file, indent=4)

    return results

if __name__ == "__main__":
    policy_file = 'inventory_policy_1.json'
    services_data = list_used_services(policy_file)
    #for category, services in services_data.items():
    #    print(f"\n{category}:")
    #    for service, data in services.items():
    #        print(f"  {service}: {data if data else 'No resources found.'}")