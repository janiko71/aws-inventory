# aws-inventory
Did your never forget to stop an EC2 instance? Or to delete some unusued AWS resource? I'm sure you did. And only remembering it when getting the bill. I know, [AWS Config](https://aws.amazon.com/config) may help you, but did you ever try? It's prohibitive!

This python script lists all the main resources of your AWS account. This inventory may be uncomplete, but it should help you to find what I call "main" resources that are, in my mind, resources that should affect billing and/or security.

Intended for personal use (even if I added some professional features like logging), and for only one account. For more information on multiple accounts, read the [wiki](https://github.com/janiko71/aws-inventory/wiki). 

**If you test this code, please send me feedback**: I can't test every configuration (especially when there are a lot of items in inventories), so either if it works or not, let me know what is fine and what needs to be corrected (use [issues](https://github.com/janiko71/aws-inventory/issues)).

Supported AWS services is limited, but I add some regulary. **Supported services are detailed [here (wiki)](https://github.com/janiko71/aws-inventory/wiki/Supported-services)**:


~~Derived from https://github.com/powerupcloud/AWSInventoryLambda but not forked because it has been too much modified.~~ Rewritten from scratch to be more _pythonified_.
## Pre-requisites
This program needs Python 3.4 or newer. 

AWS CLI must be installed and configured on the system you want to run aws-inventory. You SHOULD use a special account with minimal rights (= those in inventory*.json files). See [wiki](https://github.com/janiko71/aws-inventory/wiki) for more.

Make sure that you have the latest boto3 version. Older versions may lead to signature error with the newest regions or to some malfunction. Further information here : http://docs.aws.amazon.com/general/latest/gr/signature-version-4.html.

# What's new in this version?
This is an attempt to use multithreading in order to accelerate the script. And, at first sight, it looks better: 230 seconds instead of 960 (for the same inventory) on my first test. A lot of services has been added, with some improvements (like for Lightsail).

# And in the next one?
I'm working on a visualization tool. It can be useful for infra services (EC2, EFS, VPC, etc.). I don't know yet how far I can go, and what is the best dataviz tool for that. I'm trying with [vis.js](http://visjs.org/).

# How to use it
This script is intented to be executed from any python environment (and not only as a AWS lambda function as the original script). More information on [wiki](https://github.com/janiko71/aws-inventory/wiki).

# If you like it
This project is _open source_ (GPL-3.0), but took me some time and efforts to design, to code, to make some researches and to test it. I hope you like this script, and that it will be useful for you.

So, this project in **donationware** (or _donateware_). It means that you _can_ give me a small fee or contribution for my work. For those who are familiar with [RFCs](https://www.ietf.org/rfc/rfc2119.txt), it's not SHOULD but it's MAY. Think about it especially if you fork the project, but there is **no obligation**.

For instance, a couple of $ or € can help me buying a dozen of coffee at work! And if you are millionnaire or a big company, please note that the service I use ([leetchi.com](https://www.leetchi.com/c/janiko71-aws-inventory)) accepts millions of $/€, which could be help me with coffees until retirement.

You _can_ donate here: **[_janiko71/aws-inventory_ on leetchi.com](https://www.leetchi.com/c/janiko71-aws-inventory)**
