import boto3

res = 'organizations'
svc = 'list_accounts'
#region = 'eu-west-3'
#region = 'global'
region = None
region = 'us-north-1'

try:
    # Get the service resource
    client = boto3.client(res, region_name=region)

    # Create the queue. This returns an SQS.Queue instance
    res = client.__getattribute__(svc)()
    res.pop('ResponseMetadata', None)

    # You can now access identifiers and attributes
    print(res)

except Exception as e:

    print('-'*72)
    print(type(e), e)
    print('-'*72)
