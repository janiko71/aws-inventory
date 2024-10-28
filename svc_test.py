import boto3

res = 's3'
svc = 'list_buckets'

try:
    # Get the service resource
    client = boto3.client(res)

    # Create the queue. This returns an SQS.Queue instance
    res = client.__getattribute__(svc)()

    # You can now access identifiers and attributes
    print(res)

except Exception as e:

    print('-'*72)
    print(e)
    print('-'*72)
