# Add import for tqdm
from tqdm import tqdm

# Other imports...
import threading
import boto3
import json
import os
import sys
import re
from datetime import datetime
import time
import argparse
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

# Progress counters
total_tasks = 0
completed_tasks = 0
progress_bar = None


class InventoryThread(threading.Thread):
    """Thread class for performing inventory tasks."""

    def __init__(self, category, region, service, func, key):
        threading.Thread.__init__(self)
        self.category = category
        self.region = region
        self.service = service
        self.func = func
        self.key = key

    def run(self):
        global results, boto3_clients, completed_tasks, progress_bar
        write_log(f"Starting inventory for {self.service} in {self.region} using {self.func}")
        try:
            client_key = (self.service, self.region)
            if client_key not in boto3_clients:
                boto3_clients[client_key] = boto3.client(self.service.lower(), region_name=self.region)
            client = boto3_clients[client_key]
            
            # First sub-task: API call
            inventory = client.__getattribute__(self.func)()
            progress_bar.update(1)  # Update progress bar by 0.5 task
            
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
            results[self.category][self.service][object_type][self.region] = inventory
            progress_bar.update(1) 
        except Exception as e:
            write_log(f"Error querying {self.service} in {self.region} using {self.func}: {e}")
        finally:
            completed_tasks += 1
            write_log(f"Completed inventory for {self.service} in {self.region} using {self.func}")



def write_log(message):
    """Write a log message to the log file."""
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def get_all_regions():
    """Retrieve all AWS regions."""
    ec2 = boto3.client('ec2')
    response = ec2.describe_regions()
    return response['Regions']

def test_region_connectivity(region):
    """Test connectivity to a specific AWS region."""
    ec2 = boto3.client('ec2', region_name=region)
    try:
        ec2.describe_availability_zones()
        return True
    except Exception as e:
        write_log(f"Could not connect to the endpoint URL for region {region}: {e}")
        return False

def transform_function_name(func_name):
    """Transform a CamelCase function name to snake_case."""
    return re.sub(r'(?<!^)(?=[A-Z])', '_', func_name).lower()

def json_serial(obj):
    """JSON serializer for objects not serializable by default."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")

def create_services_structure(policy_file):
    """Create a structure of services based on the provided IAM policy file."""
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
    """List used services based on the provided IAM policy file."""
    global results, total_tasks, progress_bar

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
                        total_tasks += 1  # Increment total_tasks for each task

    # Initialize progress bar with double the total tasks
    progress_bar = tqdm(total=total_tasks * 2, desc="Inventory Progress", unit="sub-task")

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()

    progress_bar.close()

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"\nTotal execution time: {execution_time:.2f} seconds")
    
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