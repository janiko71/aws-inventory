# aws-inventory
This tool is designed to generate a (possibly) complete list (in JSON format) of assets within AWS account.
It is a fork of [aws-inventory](https://github.com/janiko71/aws-inventory/).

This repo exists as its own entity as I have particular goals to reach with this tool that might not be in line with anyone else's (e.g. products that don't cost money, or cost ridiculous amount of money, so private user won't care about those).
I also have an alergy to hashtags :) so a different formatting style all over.

# Usage.
* Create policies and attach the policies stated in inventory-policy-\* JSON files.
* Create a dedicated user and attach only those policies (all read-only to avoid unnecessary permissions escalation)

For now, the tested method is to run it locally, but the code has the potential to run as lambda + output to s3 bucket.

# progress so far.
* IAM (users, groups)
* kinesis
* athena (streams and databases)
* apigatewayv2
* shield (list protected assets)
* codepipeline
* codebuild
* (code)deploy
* fixed permissions creep (sqs.\*)

# TODO:
* merge IAM users and groups into one (break-down one way or the other) with policies. End goal - have a break-down of what policies are attached to each group/user


# Known issues.
Happened on some Windows machines - incompatible versions of the modules that just don't get updated automatically for some reason.

```
pip install --upgrade --force urllib3 chardet requests
```
