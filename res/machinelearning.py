import boto3
import botocore
import json
import config
import pprint, operator
import res.utils as utils
import res.glob as glob

"""
    Supported services   : SageMaker, Forecast
    Unsupported services : Augmented AI, CodeGuru, DevOps Guru, Comprehend, Fraud Detector,
                           Kendra, Lex, Personalize, Polly, Rekognition, Textract, Transcribe, Translate, DeepComposer,
                           DeepLens, DeepRacer, Panorama, Monitron, HealthLake, Lookout for Vision,  
                           Lookout for Equipments, Lookout for Metrics
"""
def get_sagemaker_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns SageMaker details

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: SageMaker inventory
        :rtype: json

        ..note:: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker.html
    """ 
    
    inventory = {}

    inventory['domains'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "sagemaker", 
        aws_region = "all", 
        function_name = "list_domains", 
        key_get = "Domains",
        join_key = "DomainId",
        detail_join_key = "DomainId",
        detail_function = "describe_domain",
        detail_get_key = "",
        pagination = True
    )

    # Not sure if it's relevant

    inventory['projects'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "sagemaker", 
        aws_region = "all", 
        function_name = "list_projects", 
        key_get = "ProjectSummaryList",
        join_key = "ProjectName",
        detail_join_key = "ProjectName",
        detail_function = "describe_project",
        detail_get_key = "",
        pagination = False
    )
    inventory['notebook-instances'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "sagemaker", 
        aws_region = "all", 
        function_name = "list_notebook_instances", 
        key_get = "NotebookInstances",
        join_key = "NotebookInstanceName",
        detail_join_key = "NotebookInstanceName",
        detail_function = "describe_notebook_instance",
        detail_get_key = "",
        pagination = True
    )

    return inventory

def get_forecast_inventory(oId, profile, boto3_config, selected_regions):

    """
        Returns Forecast details

        :param oId: ownerId (AWS account)
        :type oId: string
        :param profile: configuration profile name used for session
        :type profile: string

        :return: Forecast inventory
        :rtype: json

        ..note:: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/forecast.html
    """ 
    
    inventory = {}

    inventory['datasets'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "forecast", 
        aws_region = "all", 
        function_name = "list_datasets", 
        key_get = "Datasets",
        join_key = "DatasetName",
        detail_join_key = "DatasetName",
        detail_function = "describe_dataset",
        detail_get_key = "",
        pagination = True
    )

    inventory['predictors'] = glob.get_inventory(
        ownerId = oId,
        profile = profile,
        boto3_config = boto3_config,
        selected_regions = selected_regions,
        aws_service = "forecast", 
        aws_region = "all", 
        function_name = "list_predictors", 
        key_get = "Predictors",
        join_key = "PredictorName",
        detail_join_key = "PredictorName",
        detail_function = "describe_predictor",
        detail_get_key = "",
        pagination = True
    )

    return inventory

''' Hey, doc: we're in a module! '''

if (__name__ == "__main__"):
    print("Module => Do not execute")
