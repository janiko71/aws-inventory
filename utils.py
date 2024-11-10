# utils.py

import re
import os
import json
import boto3
from datetime import datetime

def write_log(message, log_file_path):
    """
    Write a log message to the log file.

    Args:
        message (str): The message to log.
        log_file_path (str): The path to the log file.
    """
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def transform_function_name(func_name):
    """
    Transform a CamelCase function name to snake_case.

    Exception : s3:ListAllMyBuckets -> list_buckets

    Args:
        func_name (str): The CamelCase function name.

    Returns:
        str: The snake_case function name.
    """
    if func_name == "ListAllMyBuckets":
        return "list_buckets"
    else:
        return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', func_name)).lower()

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

def is_empty(value):
    """
    Check if a value is empty. This includes None, empty strings, empty lists, and empty dictionaries.

    Args:
        value (any): The value to check.

    Returns:
        bool: True if the value is empty, False otherwise.
    """
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():  # Check empty string
        return True
    if isinstance(value, (list, dict)) and len(value) == 0:  # Check empty list or dict
        return True
    return False

def ensure_directory_exists(directory):
    """
    Ensure that a directory exists. If it does not exist, create it.

    Args:
        directory (str): The path to the directory.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_log_file(log_dir):
    """
    Create a timestamped log file in the specified directory.

    Args:
        log_dir (str): The directory where the log file will be created.

    Returns:
        str: The path to the created log file.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(log_dir, f"log_{timestamp}.log")

def get_all_regions():
    """
    Retrieve all AWS regions.

    Returns:
        list: A list of all AWS regions.
    """
    ec2 = boto3.client('ec2')
    response = ec2.describe_regions()
    return response['Regions']

def test_region_connectivity(region, log_file_path):
    """
    Test connectivity to a specific AWS region.

    Args:
        region (str): The AWS region to test.
        log_file_path (str): The path to the log file.

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