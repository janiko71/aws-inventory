import subprocess
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

def run_aws_cli(command):
    """Exécute une commande AWS CLI et retourne la sortie en JSON."""
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        if result.returncode == 0:
            return json.loads(result.stdout.decode('utf-8'))
        else:
            print(f"Erreur lors de l'exécution: {result.stderr.decode('utf-8')}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

def get_all_regions():
    """Récupère la liste de toutes les régions AWS."""
    command = "aws ec2 describe-regions --query 'Regions[*].RegionName'"
    regions = run_aws_cli(command)
    return regions if regions else []

def run_command_in_region(service_func, region):
    """Exécute une commande AWS CLI spécifique à un service dans une région donnée."""
    env_command = f"AWS_DEFAULT_REGION={region} {service_func()}"
    return run_aws_cli(env_command)

### Déclaration des fonctions pour chaque service AWS

# Calcul
def list_ec2_instances():
    return "aws ec2 describe-instances --query 'Reservations[*].Instances[*].InstanceId'"

def list_ecs_clusters():
    return "aws ecs list-clusters --query 'clusterArns[*]'"

def list_eks_clusters():
    return "aws eks list-clusters --query 'clusters[*]'"

def list_lambda_functions():
    return "aws lambda list-functions --query 'Functions[*].FunctionName'"

def list_lightsail_instances():
    return "aws lightsail get-instances --query 'instances[*].name'"

# Stockage
def list_s3_buckets():
    return "aws s3api list-buckets --query 'Buckets[*].Name'"

def list_ebs_volumes():
    return "aws ec2 describe-volumes --query 'Volumes[*].VolumeId'"

def list_efs_file_systems():
    return "aws efs describe-file-systems --query 'FileSystems[*].FileSystemId'"

# Bases de données
def list_rds_instances():
    return "aws rds describe-db-instances --query 'DBInstances[*].DBInstanceIdentifier'"

def list_dynamodb_tables():
    return "aws dynamodb list-tables --query 'TableNames[*]'"

def list_redshift_clusters():
    return "aws redshift describe-clusters --query 'Clusters[*].ClusterIdentifier'"

def list_elasticache_clusters():
    return "aws elasticache describe-cache-clusters --query 'CacheClusters[*].CacheClusterId'"

# Mise en réseau
def list_vpcs():
    return "aws ec2 describe-vpcs --query 'Vpcs[*].VpcId'"

def list_elb_load_balancers():
    return "aws elb describe-load-balancers --query 'LoadBalancerDescriptions[*].LoadBalancerName'"

def list_cloudfront_distributions():
    return "aws cloudfront list-distributions --query 'DistributionList.Items[*].Id'"

def list_route53_hosted_zones():
    return "aws route53 list-hosted-zones --query 'HostedZones[*].Id'"

def list_api_gateways():
    return "aws apigateway get-rest-apis --query 'items[*].id'"

# Surveillance et gestion
def list_cloudwatch_alarms():
    return "aws cloudwatch describe-alarms --query 'MetricAlarms[*].AlarmName'"

def list_cloudtrail_trails():
    return "aws cloudtrail describe-trails --query 'trailList[*].Name'"

def list_config_rules():
    return "aws configservice describe-config-rules --query 'ConfigRules[*].ConfigRuleName'"

# IAM et Sécurité
def list_iam_users():
    return "aws iam list-users --query 'Users[*].UserName'"

def list_kms_keys():
    return "aws kms list-keys --query 'Keys[*].KeyId'"

def list_secrets_manager_secrets():
    return "aws secretsmanager list-secrets --query 'SecretList[*].Name'"

def list_waf_rules():
    return "aws waf list-rules --query 'Rules[*].RuleId'"

def list_shield_protections():
    return "aws shield list-protections --query 'Protections[*].Id'"

# Machine Learning
def list_sagemaker_endpoints():
    return "aws sagemaker list-endpoints --query 'Endpoints[*].EndpointName'"

def list_rekognition_collections():
    return "aws rekognition list-collections --query 'CollectionIds[*]'"

def list_comprehend_datasets():
    return "aws comprehend list-datasets --query 'DatasetPropertiesList[*].DatasetArn'"

# Autres services
def list_sns_topics():
    return "aws sns list-topics --query 'Topics[*].TopicArn'"

def list_sqs_queues():
    return "aws sqs list-queues --query 'QueueUrls[*]'"

def list_step_functions():
    return "aws stepfunctions list-state-machines --query 'stateMachines[*].stateMachineArn'"

def list_glue_jobs():
    return "aws glue list-jobs --query 'JobNames[*]'"

def list_cloudformation_stacks():
    return "aws cloudformation describe-stacks --query 'Stacks[*].StackName'"

# Recensement des services utilisés
def list_used_services():
    """Recense les services AWS utilisés pour un compte donné dans toutes les régions disponibles."""
    regions = get_all_regions()

    if not regions:
        print("Impossible de récupérer la liste des régions.")
        return

    services = {
        # Calcul
        'EC2 Instances': list_ec2_instances,
        'ECS Clusters': list_ecs_clusters,
        'EKS Clusters': list_eks_clusters,
        'Lambda Functions': list_lambda_functions,
        'Lightsail Instances': list_lightsail_instances,
        # Stockage
        'S3 Buckets (global)': list_s3_buckets,
        'EBS Volumes': list_ebs_volumes,
        'EFS File Systems': list_efs_file_systems,
        # Bases de données
        'RDS Instances': list_rds_instances,
        'DynamoDB Tables': list_dynamodb_tables,
        'Redshift Clusters': list_redshift_clusters,
        'ElastiCache Clusters': list_elasticache_clusters,
        # Mise en réseau
        'VPCs': list_vpcs,
        'ELB Load Balancers': list_elb_load_balancers,
        'CloudFront Distributions (global)': list_cloudfront_distributions,
        'Route 53 Hosted Zones (global)': list_route53_hosted_zones,
        'API Gateways': list_api_gateways,
        # Surveillance et gestion
        'CloudWatch Alarms': list_cloudwatch_alarms,
        'CloudTrail Trails': list_cloudtrail_trails,
        'Config Rules': list_config_rules,
        # IAM et Sécurité
        'IAM Users (global)': list_iam_users,
        'KMS Keys': list_kms_keys,
        'Secrets Manager Secrets': list_secrets_manager_secrets,
        'WAF Rules': list_waf_rules,
        'Shield Protections': list_shield_protections,
        # Machine Learning
        'SageMaker Endpoints': list_sagemaker_endpoints,
        'Rekognition Collections': list_rekognition_collections,
        'Comprehend Datasets': list_comprehend_datasets,
        # Autres services
        'SNS Topics': list_sns_topics,
        'SQS Queues': list_sqs_queues,
        'Step Functions': list_step_functions,
        'Glue Jobs': list_glue_jobs,
        'CloudFormation Stacks': list_cloudformation_stacks,
    }

    results = {}

    # Utilisation de ThreadPoolExecutor pour exécuter les services en parallèle pour chaque région
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_service = {}

        # Services globaux (pas besoin de parcourir les régions)
        for service, func in services.items():
            if "global" in service:
                future_to_service[executor.submit(func)] = service
            else:
                # Pour les services régionaux, parcourir chaque région
                for region in regions:
                    future_to_service[executor.submit(run_command_in_region, func, region)] = f"{service} in {region}"

        for future in as_completed(future_to_service):
            service_name = future_to_service[future]
            try:
                data = future.result()
                if data:
                    results[service_name] = data
            except Exception as e:
                print(f"Erreur pour le service {service_name}: {e}")

    return results

if __name__ == "__main__":
    services_data = list_used_services()
    for service, data in services_data.items():
        print(f"{service}: {data if data else 'Aucune ressource trouvée.'}")
