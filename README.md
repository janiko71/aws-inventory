# Temporary version (some services are not ok)
# aws-inventory
Did your never forget to stop an EC2 instance? Or to delete some unusued AWS resource? I'm sure you did. And only remembering it when getting the bill. I know, [AWS Config](https://aws.amazon.com/config) may help you, but did you ever try? It's prohibitive!

This python script lists all the main resources of your AWS account. This inventory may be uncomplete, but it should help you to find what I call "main" resources that are, in my mind, resources that should affect billing and/or security.

Intended for personal use (even if I added some professional features like logging), and for only one account. For more information on multiple accounts, read the [wiki](https://github.com/janiko71/aws-inventory/wiki). 

**If you test this code, please send me feedback**: I can't test every configuration (especially when there are a lot of items in inventories), so either if it works or not, let me know what is fine and what needs to be corrected (use [issues](https://github.com/janiko71/aws-inventory/issues)).

Supported AWS services is limited, but I add some regulary. Until now, supported services are :
* s3
* ec2
* vpc
* network
* ebs
* lambda
* lightsail
* efs
* glacier
* rds
* ce (cost explorer, but still experimental)
* kms
* dynamodb
* apigateway
* ecs
* elasticbeanstalk
* clouddirectory
* codestar
* neptune

~~Derived from https://github.com/powerupcloud/AWSInventoryLambda but not forked because it has been too much modified.~~ Rewritten from scratch to be more _pythonified_.
## Pre-requisites
Make sure that you have the latest boto3 version. Older versions may lead to signature error with the newest regions or to some malfunction. Further information here : http://docs.aws.amazon.com/general/latest/gr/signature-version-4.html.
Some other packages are mandatory, like datetime.
# How to use it
This script is intented to be executed from any python environment (and not only as a AWS lambda function as the original script). More information on [wiki](https://github.com/janiko71/aws-inventory/wiki).
