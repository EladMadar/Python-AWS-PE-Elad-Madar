import boto3
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

def generate_resource_name(resource_type):
    """
    Generates a unique resource name using the AWS username.
    
    Parameters:
        resource_type (str): The type of AWS resource (ec2, s3, etc.).
    
    Returns:
        str: A unique resource name.
    """
    aws_username = get_aws_username()
    return f"{aws_username}-{resource_type}"

def get_aws_username():
    """
    Retrieves the AWS IAM username from the AWS CLI configuration.

    Returns:
        str: The AWS username (or "unknown-user" if it cannot be retrieved).
    """
    try:
        sts_client = boto3.client("sts")
        identity = sts_client.get_caller_identity()
        arn = identity["Arn"]
        return arn.split("/")[-1]  # Extract username from ARN
    except Exception:
        return "unknown-user"


def get_standard_tags(resource_name):
    """
    Returns standardized AWS tags for tracking resources.

    Parameters:
        resource_name (str): The name of the AWS resource.

    Returns:
        list: A list of AWS tag dictionaries.
    """
    aws_username = get_aws_username()

    return [
        {"Key": "Name", "Value": f"{aws_username}-{resource_name}"},
        {"Key": "Owner", "Value": aws_username},
        {"Key": "CreatedBy", "Value": "elad-madar-CLI"},
    ]


def get_latest_ami(os_name, instance_type):
    """
    Fetches the latest AMI ID for either Ubuntu or Amazon Linux based on instance type.

    Parameters:
        os_name (str): OS type (ubuntu or amazon-linux).
        instance_type (str): The EC2 instance type (t3.nano or t4g.nano).

    Returns:
        str: The latest AMI ID.
    """
    ec2_client = boto3.client("ec2")

    # Define architecture based on instance type
    architecture = "x86_64" if "t3" in instance_type else "arm64"

    # Define AMI filters based on OS and architecture
    ami_map = {
        "ubuntu": f"ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-{architecture}-server-*",
        "amazon-linux": f"amzn2-ami-hvm-*-{architecture}-gp2"
    }

    if os_name not in ami_map:
        print(Fore.RED + f"Error: Invalid AMI choice! Allowed: {list(ami_map.keys())}")
        return None

    response = ec2_client.describe_images(
        Owners=["amazon"],
        Filters=[
            {"Name": "name", "Values": [ami_map[os_name]]},
            {"Name": "architecture", "Values": [architecture]}
        ],
    )

    if not response["Images"]:
        print(Fore.RED + f"Error: No AMI found for {os_name} on {architecture}.")
        return None

    latest_ami = sorted(response["Images"], key=lambda x: x["CreationDate"], reverse=True)[0]["ImageId"]
    return latest_ami


def get_all_cli_instances():
    """
    Returns a list of all EC2 instances created via the CLI.

    Returns:
        list: A list of instance IDs.
    """
    ec2_client = boto3.client("ec2")

    response = ec2_client.describe_instances(
        Filters=[{"Name": "tag:CreatedBy", "Values": ["elad-madar-CLI"]}]
    )

    return [instance["InstanceId"] for reservation in response["Reservations"] for instance in reservation["Instances"]]


def get_running_cli_instances():
    """
    Returns a list of running EC2 instances created via the CLI.

    Returns:
        list: A list of running instance IDs.
    """
    ec2_client = boto3.client("ec2")

    response = ec2_client.describe_instances(
        Filters=[
            {"Name": "tag:CreatedBy", "Values": ["elad-madar-CLI"]},
            {"Name": "instance-state-name", "Values": ["running"]},
        ]
    )

    return [instance["InstanceId"] for reservation in response["Reservations"] for instance in reservation["Instances"]]


def terminate_all_resources():
    """
    Deletes all EC2 instances, S3 buckets, and Route 53 hosted zones created via CLI.
    Asks for user confirmation before proceeding.
    """
    import ec2_manager
    import s3_manager
    import route53_manager

    confirm = input(Fore.MAGENTA + "Are you sure you want to delete all CLI-created resources? (yes/no): ").strip().lower()
    if confirm != "yes":
        print(Fore.RED + "Operation canceled.")
        return

    print(Fore.RED + "\nDeleting all EC2 instances...")
    for instance_id in get_all_cli_instances():
        ec2_manager.terminate_instance(instance_id)

    print(Fore.RED + "\nDeleting all S3 buckets...")
    for bucket in s3_manager.list_buckets():
        s3_manager.delete_bucket(bucket)

    print(Fore.RED + "\nDeleting all Route 53 hosted zones...")
    for zone in route53_manager.list_zones():
        route53_manager.delete_hosted_zone(zone)

    print(Fore.GREEN + "\nAll CLI-created resources have been deleted.")

import ec2_manager
import s3_manager
import route53_manager

def list_all_resources():
    """
    Lists all AWS resources created via the CLI.
    Displays EC2 instances, S3 buckets, and Route 53 hosted zones in a structured format.
    """
    print(Fore.CYAN + "\n--- EC2 Instances ---")
    ec2_instances = ec2_manager.list_instances()
    if not ec2_instances:
        print()

    print(Fore.CYAN + "\n--- S3 Buckets ---")
    s3_buckets = s3_manager.list_buckets()
    if not s3_buckets:
        print()

    print(Fore.CYAN + "\n--- Route 53 Hosted Zones ---")
    hosted_zones = route53_manager.list_zones()
    if not hosted_zones:
        print()