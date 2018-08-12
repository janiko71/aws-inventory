import time
import logging
import json
from time import gmtime, strftime

#
# Environment Variables & File handling & logging
#
display = 'OwnerID : {} ! Region : {:16} ! {} ({})'
# --- Initial values for inventory files names
t = gmtime()
timestamp = strftime("%Y%m%d%H%M%S", t)
filepath = './output/'

# --- logging variables
log_filepath    = './log/'
logger          = logging.getLogger('aws-inventory')
hdlr            = logging.FileHandler(log_filepath+'inventory.log')
formatter       = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

# --- Log handler
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)

# --- If needed: S3 bucket name to write inventory
S3_INVENTORY_BUCKET="xx"

# --- Arguments/Supported commands
SUPPORTED_COMMANDS = ['s3','ec2','vpc','network','ebs','lambda','lightsail','efs','glacier','rds','ce','kms','dynamodb','apigateway','ecs','elasticbeanstalk',
    'clouddirectory','codestar','alexa','workmail','neptune']

# --- AWS Regions 
with open('aws_regions.json') as json_file:
    aws_regions = json.load(json_file)
regions = aws_regions.get('Regions',[]) 