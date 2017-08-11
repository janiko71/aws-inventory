# aws-inventory
This python script lists all the main resources of your AWS account. This inventory may not be complete, but it should help you to find what I call "main" resources that are, in my mind, resources that could affect billing and/or security.
Derived from https://github.com/powerupcloud/AWSInventoryLambda but not forked because it has been too much modified.
## Pre-requisites
Make sure that you have the latest boto3 version. Older versions may lead to signature error with the newest regions. Further information here : http://docs.aws.amazon.com/general/latest/gr/signature-version-4.html.
# How to use it
This script is intented to be executed from any python environment (and not only as a AWS lambda function as the original script).
