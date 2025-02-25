# AWS CLI Tool - User Guide

## Overview

This AWS CLI Tool is a command-line interface designed to manage AWS resources such as EC2 instances, S3 buckets, and Route 53 DNS records. It provides a structured way to interact with AWS services using predefined commands.

## Installation and Setup

### Prerequisites

- Python 3.7 or later (Ensure Python is installed)
- AWS CLI configured with appropriate credentials
- Required Python packages (installed via `requirements.txt`)

### Installation Steps

1. **Clone the Repository**

   ```sh
   git clone <repository-url>
   cd aws-cli-tool
   ```

2. **Create and Activate a Virtual Environment**

   ```sh
   python3 -m venv venv
   source venv/bin/activate  # On Windows use venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```sh
   pip install -r requirements.txt
   ```

4. **Configure AWS CLI Credentials**

   ```sh
   aws configure
   ```

   You will be prompted to enter:

   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region name (e.g., `us-east-1`)
   - Default output format (leave blank for `json`)

5. **Run the CLI Tool**

   ```sh
   python cli.py
   ```

## Commands and Usage

The following table outlines all possible commands and arguments:

| Command               | Arguments                                                                                | Description                                     |
| --------------------- | ---------------------------------------------------------------------------------------- | ----------------------------------------------- |
| `ec2 create`          | `--instance-type`, `--ami`, `--vpc-id`, `--subnet-id`, `--keypair`, `--public/--private` | Creates an EC2 instance                         |
| `ec2 list`            | None                                                                                     | Lists all EC2 instances                         |
| `ec2 start`           | `--instance-id`                                                                          | Starts an EC2 instance                          |
| `ec2 stop`            | `--instance-id`                                                                          | Stops an EC2 instance                           |
| `ec2 terminate`       | `--instance-id`                                                                          | Terminates an EC2 instance                      |
| `s3 create`           | `--public/--private`, `--region`                                                         | Creates an S3 bucket                            |
| `s3 list`             | None                                                                                     | Lists all S3 buckets                            |
| `s3 upload`           | `--bucket-name`, `--file-path`                                                           | Uploads a file to an S3 bucket                  |
| `s3 delete`           | `--bucket-name`                                                                          | Deletes an S3 bucket                            |
| `route53 create-zone` | `--vpc-id`, `--domain-name`                                                              | Creates a Route 53 hosted zone                  |
| `route53 list-zones`  | None                                                                                     | Lists all hosted zones                          |
| `route53 add-record`  | `--zone-id`, `--record-name`, `--record-type`, `--record-value`                          | Adds a DNS record                               |
| `route53 delete`      | `--zone-id`                                                                              | Deletes a hosted zone                           |
| `all list-all`        | None                                                                                     | Lists all AWS resources created using the CLI   |
| `all terminate-all`   | None                                                                                     | Deletes all AWS resources created using the CLI |

## File Structure and Explanation

This project consists of multiple files, each handling different AWS services.

### `cli.py` (Main CLI Handler)

- Initializes the interactive CLI session.
- Processes user commands and invokes the appropriate function from `ec2_manager.py`, `s3_manager.py`, or `route53_manager.py`.
- Handles errors and validates user inputs.

### `ec2_manager.py` (EC2 Instance Management)

- ``: Creates a new EC2 instance with specified parameters.
- ``: Lists all EC2 instances created by this CLI.
- ``: Starts a specified EC2 instance.
- ``: Stops a specified EC2 instance.
- ``: Terminates a specified EC2 instance.
- ``: Returns the count of running EC2 instances for the current AWS user.

### `s3_manager.py` (S3 Bucket Management)

- ``: Creates an S3 bucket and assigns public/private access.
- ``: Lists all S3 buckets created by this CLI.
- ``: Uploads a file to an S3 bucket.
- ``: Deletes an S3 bucket along with its contents.

### `route53_manager.py` (Route 53 DNS Management)

- ``: Creates a private hosted zone in Route 53.
- ``: Lists all hosted zones created by this CLI.
- ``: Adds a DNS record to a hosted zone.
- ``: Deletes a hosted zone after removing its records.

### `utils.py` (Utility Functions)

- ``: Generates unique resource names based on the AWS username.
- ``: Retrieves the current AWS IAM username.
- ``: Returns a set of default AWS tags for tracking resources.
- ``: Fetches the latest AMI ID for an instance type.
- ``: Retrieves all EC2 instances created by the CLI.
- ``: Retrieves all running EC2 instances created by the CLI.
- ``: Deletes all AWS resources created via this CLI.
- ``: Lists all AWS resources created by this CLI.

## Running the Compiled CLI Tool

This CLI tool can be converted into an executable using **PyInstaller**:

1. Install PyInstaller:
   ```sh
   pip install pyinstaller
   ```
2. Create an executable:
   ```sh
   pyinstaller --onefile --console --name aws-cli-tool cli.py
   ```
3. Run the compiled binary:
   ```sh
   ./dist/aws-cli-tool
   ```

## Notes

- Ensure you have the proper AWS credentials configured using `aws configure`.
- Some AWS resources may have restrictions (e.g., EC2 instance limits, IAM permissions).
- Deleting all resources via `all terminate-all` is **irreversible**.

## Conclusion

This AWS CLI Tool simplifies AWS resource management by providing a structured command-line interface. It supports EC2 instance creation, S3 bucket management, and Route 53 DNS record manipulation, making AWS operations more efficient.

