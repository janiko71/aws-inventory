import boto3
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

def run_command_in_region(service_func, region, progress):
    """
    Execute a specific boto3 API call for a service in a given region.
    
    :param service_func: Function returning the boto3 client method
    :type service_func: function
    :param region: AWS region
    :type region: str
    :param progress: A dictionary containing progress details
    :type progress: dict
    :return: JSON output of the command or None if there was an error
    :rtype: dict or None
    """
    try:
        result = service_func(region)
        progress['completed'] += 1
        if result is None:
            progress['failed'] += 1
        print(f"\rProgress: {progress['completed']}/{progress['total']} ({progress['completed'] - progress['failed']} completed, {progress['failed']} in error)", end='', flush=True)
        return result
    except Exception as e:
        write_log(f"Could not execute command for region {region}: {e}")
        progress['failed'] += 1
        return None

# Compute
def list_ec2_instances(region):
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_instances()
    return response

def list_ecs_clusters(region):
    ecs = boto3.client('ecs', region_name=region)
    response = ecs.list_clusters()
    return response

def list_eks_clusters(region):
    eks = boto3.client('eks', region_name=region)
    response = eks.list_clusters()
    return response

def list_lambda_functions(region):
    lambda_client = boto3.client('lambda', region_name=region)
    response = lambda_client.list_functions()
    return response

def list_lightsail_instances(region):
    lightsail = boto3.client('lightsail', region_name=region)
    response = lightsail.get_instances()
    return response

# Storage
def list_s3_buckets(region):
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    return response

def list_ebs_volumes(region):
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_volumes()
    return response

def list_efs_file_systems(region):
    efs = boto3.client('efs', region_name=region)
    response = efs.describe_file_systems()
    return response

# Databases
def list_rds_instances(region):
    rds = boto3.client('rds', region_name=region)
    response = rds.describe_db_instances()
    return response

def list_dynamodb_tables(region):
    dynamodb = boto3.client('dynamodb', region_name=region)
    response = dynamodb.list_tables()
    return response

def list_redshift_clusters(region):
    redshift = boto3.client('redshift', region_name=region)
    response = redshift.describe_clusters()
    return response

def list_elasticache_clusters(region):
    elasticache = boto3.client('elasticache', region_name=region)
    response = elasticache.describe_cache_clusters()
    return response

# Networking
def list_vpcs(region):
    ec2 = boto3.client('ec2', region_name=region)
    response = ec2.describe_vpcs()
    return response

def list_elb_load_balancers(region):
    elb = boto3.client('elb', region_name=region)
    response = elb.describe_load_balancers()
    return response

def list_cloudfront_distributions(region):
    cloudfront = boto3.client('cloudfront')
    response = cloudfront.list_distributions()
    return response

def list_route53_hosted_zones(region):
    route53 = boto3.client('route53')
    response = route53.list_hosted_zones()
    return response

def list_api_gateways(region):
    apigateway = boto3.client('apigateway', region_name=region)
    response = apigateway.get_rest_apis()
    return response

# Monitoring and Management
def list_cloudwatch_alarms(region):
    cloudwatch = boto3.client('cloudwatch', region_name=region)
    response = cloudwatch.describe_alarms()
    return response

def list_cloudtrail_trails(region):
    cloudtrail = boto3.client('cloudtrail', region_name=region)
    response = cloudtrail.describe_trails()
    return response

def list_config_rules(region):
    config = boto3.client('config', region_name=region)
    response = config.describe_config_rules()
    return response

# IAM and Security
def list_iam_users(region):
    iam = boto3.client('iam')
    response = iam.list_users()
    return response

def list_kms_keys(region):
    kms = boto3.client('kms', region_name=region)
    response = kms.list_keys()
    return response

def list_secrets_manager_secrets(region):
    secretsmanager = boto3.client('secretsmanager', region_name=region)
    response = secretsmanager.list_secrets()
    return response

def list_waf_rules(region):
    waf = boto3.client('waf')
    response = waf.list_rules()
    return response

def list_shield_protections(region):
    shield = boto3.client('shield')
    response = shield.list_protections()
    return response

# Machine Learning
def list_sagemaker_endpoints(region):
    sagemaker = boto3.client('sagemaker', region_name=region)
    response = sagemaker.list_endpoints()
    return response

def list_rekognition_collections(region):
    rekognition = boto3.client('rekognition', region_name=region)
    response = rekognition.list_collections()
    return response

def list_comprehend_datasets(region):
    comprehend = boto3.client('comprehend', region_name=region)
    response = comprehend.list_datasets()
    return response

# Analytics
def list_glue_jobs(region):
    glue = boto3.client('glue', region_name=region)
    response = glue.list_jobs()
    return response

# Application Integration
def list_sns_topics(region):
    sns = boto3.client('sns', region_name=region)
    response = sns.list_topics()
    return response

def list_sqs_queues(region):
    sqs = boto3.client('sqs', region_name=region)
    response = sqs.list_queues()
    return response

def list_step_functions(region):
    sfn = boto3.client('stepfunctions', region_name=region)
    response = sfn.list_state_machines()
    return response

# Management & Governance
def list_cloudformation_stacks(region):
    cloudformation = boto3.client('cloudformation', region_name=region)
    response = cloudformation.describe_stacks()
    return response

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
                    future_to_service[executor.submit(func, None)] = (category, service)
                else:
                    # For regional services, iterate over each region
                    for region in regions:
                        region_name = region['RegionName']
                        write_log(f"Querying region: {region_name}, service: {service}, function: {func.__name__}")
                        if test_region_connectivity(region_name):
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