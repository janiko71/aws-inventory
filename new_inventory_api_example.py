import threading
import boto3
import json
import os
import sys
from datetime import datetime
import time
from res.awsthread import AWSThread

# Ensure log directory exists
log_dir = "log"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Create a timestamped log file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file_path = os.path.join(log_dir, f"log_{timestamp}.log")
json_file_path = os.path.join(log_dir, f"inventory_result_{timestamp}.json")

# Global cache for boto3 clients
boto3_clients = {}

class InventoryThread(threading.Thread):
    def __init__(self, category, region, service, func, key):
        threading.Thread.__init__(self)
        self.category = category
        self.region = region
        self.service = service
        self.func = func
        self.key = key

    def run(self):
        global results, boto3_clients
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
            write_log(f"Error querying {self.key}: {e}")


def write_log(message):
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
    ec2 = boto3.client('ec2', region_name=region)
    try:
        ec2.describe_availability_zones()
        return True
    except Exception as e:
        write_log(f"Could not connect to the endpoint URL for region {region}: {e}")
        return False

# Compute
def list_ec2_instances(client):
    response = client.describe_instances()
    return response

# Inventory of used services
def list_used_services():
    """
    Inventory AWS services used for a given account across all available regions.
    
    :return: Dictionary of services and their resources grouped by categories
    :rtype: dict
    """

    global results

    start_time = time.time()
    
    regions = get_all_regions()

    if not regions:
        write_log("Unable to retrieve the list of regions.")
        return

    services = {
        'Compute': {
            'ec2': 'list_ec2_instances',
            'ec2': 'describe_vpcs',
        }
    }

    results = {}

    thread_list = []

    # Global services (no need to iterate over regions)
    for category, service_dict in services.items():
        for service, func in service_dict.items():
            if "global" in service:                
                write_log(f"Querying service: {service}, function: {func.__name__}")
                thread = InventoryThread(category, "global", service, func, {})
                results[service] = func(boto3.client(service.lower(), region_name="global"))
            else:
                # For regional services, iterate over each region
                for region in regions:
                    region_name = region['RegionName']
                    if test_region_connectivity(region_name):
                        thread = InventoryThread(category, region_name, service, func, {})
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
    services_data = list_used_services()
    for category, services in services_data.items():
        print(f"\n{category}:")
        for service, data in services.items():
            print(f"  {service}: {data if data else 'No resources found.'}")