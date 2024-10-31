import boto3
import botocore
from botocore.exceptions import EndpointConnectionError

res = 'privatenetworks'
svc = 'list_networks'
#region = 'eu-west-3'
#region = None
region = 'us-east-1'
#region = 'global'

def print_exception(order, e):
    print('-'*72)
    print(order, type(e), e)
    print('-'*72) 

try:
    # Get the service resource
    client = boto3.client(res, region_name=region)

    # Create the queue. This returns an SQS.Queue instance
    res = client.__getattribute__(svc)()
    res.pop('ResponseMetadata', None)

    # You can now access identifiers and attributes
    print(res)

#except AWSOrganizationsNotInUseException as e1:
#    print_exception(1, e1)
except AttributeError as e2:
    print_exception(2, e2)
except botocore.exceptions.ClientError as e3:
    print_exception(3, e3)
except EndpointConnectionError as e4:
    print_exception(4, e4)
except Exception as e:
    print_exception(5, e)

