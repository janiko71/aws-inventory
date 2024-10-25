import subprocess
import json
import os
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Ensure log directory exists
log_dir = "log"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Create a timestamped log file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file_path = os.path.join(log_dir, f"log_{timestamp}.log")
json_file_path = os.path.join(log_dir, f"inventory_result_{timestamp}.json")

def write_log(message):
    with open(log_file_path, "a") as log_file:
        log_file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def run_aws_cli(command):
    """
    Execute an AWS CLI command and return the output in JSON.
    
    :param command: AWS CLI command to execute
    :type command: str
    :return: JSON output of the command or None if there was an error
    :rtype: dict or None
    """
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        if result.returncode == 0:
            write_log(f"Success: {command}")
            return json.loads(result.stdout.decode('utf-8'))
        else:
            error_message = result.stderr.decode('utf-8')
            write_log(f"Error: {command} - {error_message}")
            return None
    except Exception as e:
        write_log(f"Exception: {command} - {e}")
        return None

def get_all_regions():
    """
    Retrieve the list of all AWS regions.
    
    :return: List of all AWS regions
    :rtype: list
    """
    command = "aws ec2 describe-regions --output json"
    regions = run_aws_cli(command)
    return regions['Regions'] if regions else []

def test_region_connectivity(region):
    command = f"aws ec2 describe-availability-zones --region {region}"
    return run_aws_cli(command)

def run_command_in_region(service_func, region, progress):
    """
    Execute a specific AWS CLI command for a service in a given region.
    
    :param service_func: Function returning the AWS CLI command
    :type service_func: function
    :param region: AWS region
    :type region: str
    :param progress: A dictionary containing progress details
    :type progress: dict
    :return: JSON output of the command or None if there was an error
    :rtype: dict or None
    """
    try:
        env_command = f"AWS_DEFAULT_REGION={region} {service_func()}"
        result = run_aws_cli(env_command)
        progress['completed'] += 1
        if result is None:
            progress['failed'] += 1
        print(f"\rProgress: {progress['completed']}/{progress['total']} ({progress['completed'] - progress['failed']} completed, {progress['failed']} in error)", end='', flush=True)
        return result
    except Exception as e:
        write_log(f"Could not execute command for region {region}: {e}")
        return None

### Declaration of functions for each AWS service

# Compute
def list_ec2_instances():
    return "aws ec2 describe-instances --output json"

def list_ecs_clusters():
    return "aws ecs list-clusters --output json"

def list_eks_clusters():
    return "aws eks list-clusters --output json"

def list_lambda_functions():
    return "aws lambda list-functions --output json"

def list_lightsail_instances():
    return "aws lightsail get-instances --output json"

# Storage
def list_s3_buckets():
    return "aws s3api list-buckets --output json"

def list_ebs_volumes():
    return "aws ec2 describe-volumes --output json"

def list_efs_file_systems():
    return "aws efs describe-file-systems --output json"

# Databases
def list_rds_instances():
    return "aws rds describe-db-instances --output json"

def list_dynamodb_tables():
    return "aws dynamodb list-tables --output json"

def list_redshift_clusters():
    return "aws redshift describe-clusters --output json"

def list_elasticache_clusters():
    return "aws elasticache describe-cache-clusters --output json"

# Networking
def list_vpcs():
    return "aws ec2 describe-vpcs --output json"

def list_elb_load_balancers():
    return "aws elb describe-load-balancers --output json"

def list_cloudfront_distributions():
    return "aws cloudfront list-distributions --output json"

def list_route53_hosted_zones():
    return "aws route53 list-hosted-zones --output json"

def list_api_gateways():
    return "aws apigateway get-rest-apis --output json"

# Monitoring and Management
def list_cloudwatch_alarms():
    return "aws cloudwatch describe-alarms --output json"

def list_cloudtrail_trails():
    return "aws cloudtrail describe-trails --output json"

def list_config_rules():
    return "aws configservice describe-config-rules --output json"

# IAM and Security
def list_iam_users():
    return "aws iam list-users --output json"

def list_kms_keys():
    return "aws kms list-keys --output json"

def list_secrets_manager_secrets():
    return "aws secretsmanager list-secrets --output json"

def list_waf_rules():
    return "aws waf list-rules --output json"

def list_shield_protections():
    return "aws shield list-protections --output json"

# Machine Learning
def list_sagemaker_endpoints():
    return "aws sagemaker list-endpoints --output json"

def list_rekognition_collections():
    return "aws rekognition list-collections --output json"

def list_comprehend_datasets():
    return "aws comprehend list-datasets --output json"

# Analytics
def list_glue_jobs():
    return "aws glue list-jobs --output json"

# Application Integration
def list_sns_topics():
    return "aws sns list-topics --output json"

def list_sqs_queues():
    return "aws sqs list-queues --output json"

def list_step_functions():
    return "aws stepfunctions list-state-machines --output json"

# Management & Governance
def list_cloudformation_stacks():
    return "aws cloudformation describe-stacks --output json"

# Inventory of used services
def list_used_services():
    """
    Inventory AWS services used for a given account across all available regions.
    
    :return: Dictionary of services and their resources grouped by categories
    :rtype: dict
    """
    start_time = time.time()
    
    regions = get_all_regions()

    if not regions:
        write_log("Unable to retrieve the list of regions.")
        return

    services = {
        'Compute': {
            'EC2 Instances': list_ec2_instances,
            'ECS Clusters': list_ecs_clusters,
            'EKS Clusters': list_eks_clusters,
            'Lambda Functions': list_lambda_functions,
            'Lightsail Instances': list_lightsail_instances,
        },
        'Storage': {
            'S3 Buckets (global)': list_s3_buckets,
            'EBS Volumes': list_ebs_volumes,
            'EFS File Systems': list_efs_file_systems,
        },
        'Databases': {
            'RDS Instances': list_rds_instances,
            'DynamoDB Tables': list_dynamodb_tables,
            'Redshift Clusters': list_redshift_clusters,
            'ElastiCache Clusters': list_elasticache_clusters,
        },
        'Networking': {
            'VPCs': list_vpcs,
            'ELB Load Balancers': list_elb_load_balancers,
            'CloudFront Distributions (global)': list_cloudfront_distributions,
            'Route 53 Hosted Zones (global)': list_route53_hosted_zones,
            'API Gateways': list_api_gateways,
        },
        'Monitoring and Management': {
            'CloudWatch Alarms': list_cloudwatch_alarms,
            'CloudTrail Trails': list_cloudtrail_trails,
            'Config Rules': list_config_rules,
        },
        'IAM and Security': {
            'IAM Users (global)': list_iam_users,
            'KMS Keys': list_kms_keys,
            'Secrets Manager Secrets': list_secrets_manager_secrets,
            'WAF Rules': list_waf_rules,
            'Shield Protections': list_shield_protections,
        },
        'Machine Learning': {
            'SageMaker Endpoints': list_sagemaker_endpoints,
            'Rekognition Collections': list_rekognition_collections,
            'Comprehend Datasets': list_comprehend_datasets,
        },
        'Analytics': {
            'Glue Jobs': list_glue_jobs,
        },
        'Application Integration': {
            'SNS Topics': list_sns_topics,
            'SQS Queues': list_sqs_queues,
            'Step Functions': list_step_functions,
        },
        'Management & Governance': {
            'CloudFormation Stacks': list_cloudformation_stacks,
        }
    }

    results = {}

    # Initialize progress counter
    total_services = sum(len(service_dict) for service_dict in services.values())
    completed_services = 0
    correct_total = total_services * len(regions)
    progress = {'completed': completed_services, 'failed': 0, 'total': correct_total}

    # Use ThreadPoolExecutor to execute services in parallel for each region
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_service = {}

        # Global services (no need to iterate over regions)
        for category, service_dict in services.items():
            for service, func in service_dict.items():
                if "global" in service:
                    write_log(f"Querying service: {service}, function: {func.__name__}")
                    future_to_service[executor.submit(func)] = (category, service)
                else:
                    # For regional services, iterate over each region
                    for region in regions:
                        region_name = region['RegionName']
                        write_log(f"Querying region: {region_name}, service: {service}, function: {func.__name__}")
                        result = test_region_connectivity(region_name)
                        if result is None:
                            write_log(f"Could not connect to the endpoint URL for region {region_name}")
                        else:
                            future_to_service[executor.submit(run_command_in_region, func, region_name, progress)] = (category, f"{service} in {region_name}")

        for future in as_completed(future_to_service):
            category, service_name = future_to_service[future]
            try:
                data = future.result()
                if data:
                    if category not in results:
                        results[category] = {}
                    results[category][service_name] = data
            except Exception as e:
                write_log(f"Error for service {service_name}: {e}")

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