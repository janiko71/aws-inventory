# AWS Inventory

## Overview
Did your never forget to stop an EC2 instance? Or to delete some unusued AWS resource? I'm sure you did. And only remembering it when getting the bill. I know, [AWS Config](https://aws.amazon.com/config) may help you, but did you ever try? It's prohibitive!

This python script lists all the main resources of your AWS account. This inventory may be uncomplete, but it should help you to find what I call "main" resources that are, in my mind, resources that should affect billing and/or security.

> **This is a brand new version, completely rebuilt from scratch (again). It may be quicker and a bit simpler to maintain, but the inventory may have sometimes less details than the previous one.**

Intended for personal use (even if I added some professional features like logging), and for only one account. For more information on multiple accounts, read the [wiki](https://github.com/janiko71/aws-inventory/wiki). 

This project provides a comprehensive inventory of AWS services used within an account across all available regions. It leverages multithreading to perform inventory operations concurrently, ensuring efficient and timely data collection.

This project is *[donateware](#if-you-like-it)*. 

## Features

- **Multithreading**: Concurrently performs inventory operations to speed up data collection.
- **Service Coverage**: Supports a wide range of AWS services, including EC2, S3, RDS, Lambda, and more.
- **Policy Management**: Reads and merges IAM policy files to determine the necessary permissions for inventory operations.
- **Logging**: Detailed logging of operations and errors for troubleshooting and auditing purposes.
- **Output**: Generates JSON files with the inventory results, including metadata if specified.

## Project Structure

tbd

## Getting Started

### Prerequisites

- Python 3.11+
- AWS CLI configured with appropriate credentials
- Install required Python packages:
  ```sh
  pip install -r requirements.txt
  ```  
## Usage
1. Create Policy Files:
python create_policy_files.py
1. Run Inventory
python new_inventory_api.py --policy-dir policies --with-meta --with-extra --with-empty

### Arguments
* ```--policy-dir``` : Directory containing the IAM policy files (default: policies).
* ```--with-meta``` : Include metadata in the inventory.
* ```--with-extra``` : Include Availability Zones, Regions, and Account Attributes in the inventory.
* ```--with-empty``` : Include empty values in the inventory.

## Pre-requisites
This program needs Python 3.4 or newer. 

AWS CLI must be installed and configured on the system you want to run aws-inventory. You SHOULD use a special account with minimal rights (= those in inventory*.json files). See [wiki](https://github.com/janiko71/aws-inventory/wiki) for more.

Make sure that you have the latest boto3 version. Older versions may lead to signature error with the newest regions or to some malfunction. Further information here : 
* http://docs.aws.amazon.com/general/latest/gr/signature-version-4.html.

## How to contribute?
[**TESTERS WANTED! If you test this code, please send me feedback**](https://github.com/janiko71/aws-inventory/discussions/39): I can't test every configuration (especially when there are a lot of items in inventories), so either if it works or not, let me know what is fine and what needs to be corrected (use [issues](https://github.com/janiko71/aws-inventory/issues)).

## How to use it
This script is intented to be executed from any python environment (and not only as a AWS lambda function as the original script). More information on [wiki](https://github.com/janiko71/aws-inventory/wiki).

## If you like it
This project is _open source_ (GPL-3.0), but took me some time and efforts to design, to code, to make some researches and to test it. I hope you like this script, and that it will be useful for you.

So, this project in **donationware** (or _donateware_). It means that you _can_ give me a small fee or contribution for my work. For those who are familiar with [RFCs](https://www.ietf.org/rfc/rfc2119.txt), it's not SHOULD but it's MAY. Think about it especially if you fork the project, but there is **no obligation**.

For instance, a couple of \$ or € can help me buying a dozen of coffee at work! You can donate through the [github sponsor program](https://github.com/sponsors/janiko71).

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the terms of the GNU General Public License v3.0. See the LICENSE file for details.

## To do : services with details

- [ ] EC2, ... : ...
- [ ] ECS, list_clusters : list_services, list_tasks, describe_cluster, describe_tasks, list_tasks
- [ ] ECS, list_container_instances : describe_container_instances
- [ ] EKS, list_clusters, id : ListFargateProfiles
- [ ] EKS, list_nodegroups : describe_nodegroup, ListNodegroups
- [ ] glue, list_tables : list_schemas, list_nodegroups, list_fragate_pofile, ListTables, ListStatements
- [ ] batch:DescribeJobQueues : list_jobs (queue name)
- [ ] rekognition : list_users
