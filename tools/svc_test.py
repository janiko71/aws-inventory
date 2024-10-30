import boto3

res = 's3'
#res = 'iam'
svc = 'list_buckets'
#svc = 'list_users'
#region = 'eu-west-3'
#region = 'global'
region = None

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
    print(e)
    print('-'*72)
