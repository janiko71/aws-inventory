import threading
import boto3
import json
import os
import sys
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

# Global cache for boto3 clients
boto3_clients = {}

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
            write_log(f"Error querying {self.key}: {e}")
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
    :return: True if the region is reachable, False otherwise
    :rtype: bool
    """
    ec2 = boto3.client('ec2', region_name=region)
    try:
        ec2.describe_availability_zones()
        return True
    except Exception as e:
        write_log(f"Could not connect to the endpoint URL for region {region}: {e}")
        return False

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

    # Define the services and their corresponding functions
    services = {
        'Compute': {
            'ec2': [
                'describe_instances',
                'describe_volumes',
                'describe_snapshots',
                'describe_security_groups',
                'describe_key_pairs',
                'describe_addresses',
                'describe_network_interfaces',
                'describe_route_tables',
                'describe_subnets',
                'describe_vpcs',
                'describe_elastic_gpus',
                'describe_internet_gateways',
                'describe_ipv6_pools',
                'describe_nat_gateways',
                'describe_account_attributes',
                'describe_availability_zones',
                'describe_bundle_tasks',
                'describe_capacity_reservations',
                'describe_classic_link_instances',
                'describe_conversion_tasks',
                'describe_customer_gateways',
                'describe_dhcp_options',
                'describe_egress_only_internet_gateways',
                'describe_export_tasks',
                'describe_fleets',
                'describe_flow_logs',
                'describe_fpga_images',
                'describe_host_reservation_offerings',
                'describe_host_reservations',
                'describe_hosts',
                'describe_iam_instance_profile_associations',
                'describe_id_format',
                'describe_identity_id_format',
                'describe_image_attribute',
                'describe_images',
                'describe_import_image_tasks',
                'describe_import_snapshot_tasks',
                'describe_instance_attribute',
                'describe_instance_credit_specifications',
                'describe_instance_status',
                'describe_instances',
                'describe_internet_gateways',
                'describe_key_pairs',
                'describe_launch_template_versions',
                'describe_launch_templates',
                'describe_moving_addresses',
                'describe_nat_gateways',
                'describe_network_acls',
                'describe_network_interface_attribute',
                'describe_network_interface_permissions',
                'describe_network_interfaces',
                'describe_placement_groups',
                'describe_prefix_lists',
                'describe_regions',
                'describe_reserved_instances',
                'describe_reserved_instances_listings',
                'describe_reserved_instances_modifications',
                'describe_reserved_instances_offerings',
                'describe_route_tables',
                'describe_scheduled_instance_availability',
                'describe_scheduled_instances',
                'describe_security_group_references',
                'describe_security_groups',
                'describe_snapshot_attribute',
                'describe_snapshots',
                'describe_spot_datafeed_subscription',
                'describe_spot_fleet_instances',
                'describe_spot_fleet_request_history',
                'describe_spot_fleet_requests',
                'describe_spot_instance_requests',
                'describe_spot_price_history',
                'describe_stale_security_groups',
                'describe_subnets',
                'describe_tags',
                'describe_volume_attribute',
                'describe_volume_status',
                'describe_volumes',
                'describe_vpc_attribute',
                'describe_vpc_classic_link',
                'describe_vpc_classic_link_dns_support',
                'describe_vpc_endpoint_connection_notifications',
                'describe_vpc_endpoint_connections',
                'describe_vpc_endpoint_service_configurations',
                'describe_vpc_endpoint_service_permissions',
                'describe_vpc_endpoint_services',
                'describe_vpc_endpoints',
                'describe_vpc_peering_connections',
                'describe_vpcs',
                'describe_vpn_connections',
                'describe_vpn_gateways',
            ]
        }
    }
    results = {}
    thread_list = []

    # Iterate over each service and region
    nb_inventories = 0
    with ThreadPoolExecutor(max_workers=20) as executor:
        for category, service_dict in services.items():
            for service, funcs in service_dict.items():
                for func in funcs:
                    for region in regions:
                        region_name = region['RegionName']
                        if test_region_connectivity(region_name):
                            thread = InventoryThread(category, region_name, service, func, service)
                            nb_inventories += 1
                            print(f"Starting inventory #{nb_inventories} for {service} in {region_name} using {func}")
                            thread_list.append(thread)
                            executor.submit(thread.run)

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"\nTotal execution time: {execution_time:.2f} seconds")
    
    # Save the results to a JSON file in the output directory
    with open(json_file_path, "w") as json_file:
        json.dump(results, json_file, indent=4)

    return results

if __name__ == "__main__":
    services_data = list_used_services()