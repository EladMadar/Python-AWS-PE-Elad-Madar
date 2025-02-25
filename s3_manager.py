import boto3
import utils

import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

s3_client = boto3.client("s3")

def create_bucket(public, region="us-east-1"):
    """
    Creates an S3 bucket in a specific AWS region with default tags.

    Parameters:
        public (bool): Whether the bucket should be public.
        region (str): AWS region for the S3 bucket (default: us-east-1).
    """
    aws_username = utils.get_aws_username()  # Retrieve AWS username
    bucket_name = f"{utils.generate_resource_name('s3')}"

    # AWS does NOT allow `CreateBucketConfiguration` for us-east-1, so remove it in that case.
    if region == "us-east-1":
        s3_client.create_bucket(Bucket=bucket_name)
    else:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": region}
        )

    # Apply default tags
    s3_client.put_bucket_tagging(
        Bucket=bucket_name,
        Tagging={"TagSet": [
            {"Key": "Name", "Value": bucket_name},
            {"Key": "Owner", "Value": aws_username},
            {"Key": "CreatedBy", "Value": "elad-madar-CLI"},
        ]}
    )

    # Handle public access
    if public:
        confirm = input(Fore.RED + f"Are you sure you want to make {bucket_name} public? (yes/no): ").strip().lower()
        if confirm == "yes":
            s3_client.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={"BlockPublicAcls": False, "IgnorePublicAcls": False}
            )
            print(Fore.GREEN + f"S3 Bucket {bucket_name} is now public.")
        else:
            print(Fore.GREEN + f"S3 Bucket {bucket_name} remains private.")

    print(Fore.GREEN + f"S3 Bucket Created: {bucket_name} (Region: {region})")
    return bucket_name


def upload_file(bucket_name, file_path):
    """
    Uploads a file to an S3 bucket created via the CLI.
    
    Parameters:
        bucket_name (str): Name of the S3 bucket.
        file_path (str): Path of the file to upload.
    """
    try:
        file_name = file_path.split("/")[-1]  # Extract filename from path
        s3_client.upload_file(file_path, bucket_name, file_name)
        print(Fore.GREEN + f"File '{file_name}' uploaded to S3 bucket {bucket_name}.")
    except Exception as e:
        print(Fore.RED + f"Error uploading file: {e}")


def delete_bucket(bucket_name):
    """
    Deletes an S3 bucket and all its objects after user confirmation.
    
    Parameters:
        bucket_name (str): Name of the S3 bucket.
    """
    confirm = input(f"Are you sure you want to delete S3 bucket {bucket_name}? (yes/no): ").strip().lower()
    if confirm == "yes":
        # Delete all objects in the bucket before deleting the bucket itself
        objects = s3_client.list_objects_v2(Bucket=bucket_name)
        if "Contents" in objects:
            for obj in objects["Contents"]:
                s3_client.delete_object(Bucket=bucket_name, Key=obj["Key"])
                print(Fore.MAGENTA + f"Deleted object: {obj['Key']} from {bucket_name}")

        s3_client.delete_bucket(Bucket=bucket_name)
        print(Fore.GREEN + f"S3 bucket {bucket_name} has been deleted.")
    else:
        print(Fore.RED + "Operation canceled.")


def list_buckets():
    """
    Lists all S3 buckets created by this CLI (matching the AWS username scheme).
    
    Returns:
        list: A list of S3 bucket names.
    """
    aws_username = utils.get_aws_username()
    response = s3_client.list_buckets()

    cli_buckets = [
        bucket["Name"] for bucket in response["Buckets"]
        if bucket["Name"].startswith(f"{aws_username}-s3-")
    ]

    if cli_buckets:
        print(Fore.CYAN + "S3 Buckets created by CLI:")
        for bucket in cli_buckets:
            print(Fore.CYAN + f"  - {bucket}")
    else:
        print(Fore.RED + "No CLI-created S3 buckets found.")

    return cli_buckets