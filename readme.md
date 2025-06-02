# AWS Inventory

> **This is a brand new version, completely rebuilt from scratch (again) in nov. 2024. It may be quicker and a bit simpler to maintain, but the inventory may have sometimes less details than the previous one.**

## Overview
Did your never forget to stop an EC2 instance? Or to delete some unusued AWS resource? I'm sure you did. And only remembering it when getting the bill. I know, [AWS Config](https://aws.amazon.com/config) may help you, but did you ever try? It's prohibitive! This python script **lists all the main resources** owned within your AWS account. This inventory may be uncomplete, but it should help you to find what I call _main_ resources that are, in my mind, resources that should affect billing and/or security.

Intended for _personal_ and _non-professional_ use (even if I added some professional features like logging), and for only one account. For more information on multiple accounts, read the [wiki](https://github.com/janiko71/aws-inventory/wiki). This script provides a comprehensive inventory of AWS services used within a **single account** across all available regions. It leverages multithreading to perform inventory operations concurrently, ensuring efficient and timely data collection.

## Support Me

This project is *[donateware](https://github.com/sponsors/janiko71)*. If you like my work, consider supporting me via GitHub Sponsors!

[![Sponsor](https://img.shields.io/badge/Sponsor-GitHub-ff69b4?logo=github)](https://github.com/sponsors/janiko71)

## Main features

- **Multithreading**: Concurrently performs inventory operations to speed up data collection.
- **Service Coverage**: Supports a wide range of AWS services, including EC2, S3, RDS, Lambda, and more.
- **Extendability**: All resources and details inventory services are in JSON files. No need to write code to add new ressources!
- **Policy Management**: Reads and merges IAM policy files to determine the necessary permissions for inventory operations directly from JSON files used in the project.
- **Logging**: Detailed logging of operations and errors for troubleshooting and auditing purposes. Ensures the existence of log and output directories, and creates a timestamped log file.
- **Inventory Processes**:
  * Retrieves all AWS regions and tests connectivity.
  * Creates a service structure based on IAM policy files.
  * Compiles and logs results, handles errors, and updates progress.
- **Output**: Generates JSON files with the inventory results, including metadata if specified.

The script functionally processes AWS service inventory with detailed logging, multi-threading, and customizable options via command-line arguments.

## Getting Started

### Prerequisites

- Python 3.11+
- AWS CLI configured with appropriate credentials (see [wiki](https://github.com/janiko71/aws-inventory/wiki))
- Install required Python packages:
  ```sh
  pip install -r requirements.txt
  ```  
### Usage
Please see **[wiki](https://github.com/janiko71/aws-inventory/wiki)**.

## How to contribute?

### Testing
[**TESTERS WANTED! If you test this code, please send me feedback**](https://github.com/janiko71/aws-inventory/discussions/39): I can't test every configuration (especially when there are a lot of items in inventories), so either if it works or not, let me know what is fine and what needs to be corrected (use [issues](https://github.com/janiko71/aws-inventory/issues)).

### Writing some stuff
Contributions are welcome! Please fork the repository and submit a pull request.

### License
This project is licensed under the terms of the GNU General Public License v3.0. See the LICENSE file for details.

----

And to boost my ego, here are evaluations of my code by artificial intelligences:

## ChatGPT

### 🏁 Summary Evaluation

| Criterion                | Score / 5 | Comments                                               |
|--------------------------|------------|--------------------------------------------------------|
| Readability              | 4.5        | Very clean and well-structured code                   |
| Robustness               | 4.0        | Good error handling, but with room for improvement    |
| Extensibility            | 5.0        | JSON-based config, modular logic                      |
| Security                 | 3.5        | Use of `eval`, IAM permissions not fully validated    |
| Performance              | 4.5        | Effective use of threading                            |
| Testing & CI             | 2.0        | No automated tests present                            |
| Documentation (inline)  | 3.0        | No docstrings, but comments are present               |

> 🎯 **Overall Score**: **4 / 5** – A solid, technically sound script suitable for internal or technical use. With improvements in modularization, inline documentation, and testing, it could be elevated to a fully maintainable and production-ready tool.

## Claude AI

### 📋 **Technical Assessment**

### **Architecture** (8/10)
- [x] Modular design with threading (ThreadPoolExecutor)
- [x] Clean class structure and data organization
- [ ] Too many global variables (12 globals)
- [ ] Configuration not externalized

### **Robustness** (7/10)
- [x] AWS-specific error handling and detailed logging
- [x] Progress tracking and graceful failure handling
- [ ] Missing retry logic and rate limiting
- [ ] Generic exception handling too broad

### **Performance** (7/10)
- [x] Efficient parallelization and performance metrics
- [x] Smart global vs regional resource handling
- [ ] Memory issues for large inventories
- [ ] No explicit pagination handling

### **Maintainability** (6/10)
- [x] Readable code with good documentation
- [x] Consistent naming and logical organization
- [ ] Code duplication in `detail_handling()`
- [ ] No unit tests, hard-coded values

### **Security** (8/10)
- [x] Secure boto3/IAM credential handling
- [x] Read-only operations, no sensitive data exposure
- [ ] No permission validation
- [ ] Resource names in logs could be sensitive

### 💡 **Overall Assessment**

**Final Score: 7.2/10**

**Status: APPROVED for production**

**Strengths:** Professional architecture, excellent AWS integration, robust logging
**Key Issues:** Memory optimization needed, code refactoring required, missing retry logic
