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
   git clone https://github.com/EladMadar/Python-AWS-PE-Elad-Madar.git
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

4. **Run the CLI Tool**
   ```sh
   python cli.py
   ```

## Commands and Usage
The following table outlines all possible commands and arguments:

| Command | Arguments | Description |
|---------|----------|-------------|
| `ec2 create` | `--instance-type`, `--ami`, `--vpc-id`, `--subnet-id`, `--keypair`, `--public/--private` | Creates an EC2 instance |
| `ec2 list` | None | Lists all EC2 instances |
| `ec2 start` | `--instance-id` | Starts an EC2 instance |
| `ec2 stop` | `--instance-id` | Stops an EC2 instance |
| `ec2 terminate` | `--instance-id` | Terminates an EC2 instance |
| `s3 create` | `--public/--private`, `--region` | Creates an S3 bucket |
| `s3 list` | None | Lists all S3 buckets |
| `s3 upload` | `--bucket-name`, `--file-path` | Uploads a file to an S3 bucket |
| `s3 delete` | `--bucket-name` | Deletes an S3 bucket |
| `route53 create-zone` | `--vpc-id`, `--domain-name` | Creates a Route 53 hosted zone |
| `route53 list-zones` | None | Lists all hosted zones |
| `route53 add-record` | `--zone-id`, `--record-name`, `--record-type`, `--record-value` | Adds a DNS record (currently supports A, CNAME, TXT, record types)|
| `route53 delete` | `--zone-id` | Deletes a hosted zone |
| `all list-all` | None | Lists all AWS resources created using the CLI |
| `all terminate-all` | None | Deletes all AWS resources created using the CLI |

## File Structure and Explanation
This project consists of multiple files, each handling different AWS services.

### `cli.py` (Main CLI Handler)
- `main()`: Initializes the interactive CLI session.
- `process_command(args)`: Processes user commands and invokes the appropriate function from `ec2_manager.py`, `s3_manager.py`, or `route53_manager.py`.

### `ec2_manager.py` (EC2 Instance Management)
- `create_instance(instance_type, os_name, vpc_id=None, subnet_id=None, assign_public_ip=True, keypair_name=None)`: Creates a new EC2 instance with specified parameters.
- `list_instances()`: Lists all EC2 instances created by this CLI.
- `start_instance(instance_id)`: Starts a specified EC2 instance.
- `stop_instance(instance_id)`: Stops a specified EC2 instance.
- `terminate_instance(instance_id)`: Terminates a specified EC2 instance.
- `get_running_instances_count()`: Returns the count of running EC2 instances for the current AWS user.

### `s3_manager.py` (S3 Bucket Management)
- `create_bucket(public, region)`: Creates an S3 bucket and assigns public/private access.
- `list_buckets()`: Lists all S3 buckets created by this CLI.
- `upload_file(bucket_name, file_path)`: Uploads a file to an S3 bucket.
- `delete_bucket(bucket_name)`: Deletes an S3 bucket along with its contents.

### `route53_manager.py` (Route 53 DNS Management)
- `create_hosted_zone(vpc_id, domain_name=None)`: Creates a private hosted zone in Route 53.
- `list_zones()`: Lists all hosted zones created by this CLI.
- `add_dns_record(zone_id, record_name, record_type, record_value)`: Adds a DNS record to a hosted zone.
- `delete_hosted_zone(zone_id)`: Deletes a hosted zone after removing its records.

### `utils.py` (Utility Functions)
- `generate_resource_name(resource_type)`: Generates unique resource names based on the AWS username.
- `get_aws_username()`: Retrieves the current AWS IAM username.
- `get_standard_tags(resource_name)`: Returns a set of default AWS tags for tracking resources.
- `get_latest_ami(os_name, instance_type)`: Fetches the latest AMI ID for an instance type.
- `get_all_cli_instances()`: Retrieves all EC2 instances created by the CLI.
- `get_running_cli_instances()`: Retrieves all running EC2 instances created by the CLI.
- `terminate_all_resources()`: Deletes all AWS resources created via this CLI.
- `list_all_resources()`: Lists all AWS resources created by this CLI.

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

## Configuring AWS CLI Credentials
Before using the AWS CLI tool, you need to configure your AWS credentials.

1. **Install AWS CLI** (if not already installed):
   ```sh
   brew install awscli  # macOS
   sudo apt install awscli  # Ubuntu/Debian
   choco install awscli  # Windows
   ```

2. **Configure AWS Credentials**
   ```sh
   aws configure
   ```
   - Enter your **AWS Access Key ID**
   - Enter your **AWS Secret Access Key**
   - Specify the default AWS **region** (e.g., `us-east-1`)
   - Specify the default **output format** (`json`, `table`, or `text`)

## Notes
- Ensure you have the proper AWS credentials configured using `aws configure`.
- Some AWS resources may have restrictions (e.g., EC2 instance limits, IAM permissions).
- Deleting all resources via `all terminate-all` is **irreversible**.

## Conclusion
This AWS CLI Tool simplifies AWS resource management by providing a structured command-line interface. It supports EC2 instance creation, S3 bucket management, and Route 53 DNS record manipulation, making AWS operations more efficient.
