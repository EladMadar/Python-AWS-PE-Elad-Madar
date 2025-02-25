import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import argparse
import colorama
from colorama import Fore

try:
    import ec2_manager
    import s3_manager
    import route53_manager
    from utils import terminate_all_resources, list_all_resources
except ModuleNotFoundError as e:
    print(f"Error: {e}")
    sys.exit(1)

colorama.init(autoreset=True)

def main():
    """Runs an interactive CLI session that stays open."""
    print(Fore.CYAN + "\nAWS CLI Tool - Interactive Mode")
    print(Fore.CYAN + "Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input(Fore.YELLOW + "aws-cli> ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print(Fore.GREEN + "Exiting AWS CLI Tool.")
                break
            if not user_input:
                continue

            args = user_input.split()
            process_command(args)

        except KeyboardInterrupt:
            print(Fore.RED + "\nInterrupted. Type 'exit' to quit.")

def process_command(args):
    """Processes CLI commands just like argparse normally would."""
    parser = argparse.ArgumentParser(description="AWS Resource Provisioning CLI")
    subparsers = parser.add_subparsers(dest="resource", help="Resource type (ec2, s3, route53, all)")

    # EC2 subcommands
    ec2_parser = subparsers.add_parser("ec2", help="Manage EC2 instances")
    ec2_parser.add_argument("action", choices=["create", "start", "stop", "terminate", "list"], help="Action to perform", nargs="?")
    ec2_parser.add_argument("--instance-type", choices=["t3.nano", "t4g.nano"], help="Instance type (required for 'create')")
    ec2_parser.add_argument("--ami", choices=["ubuntu", "amazon-linux"], help="AMI type (required for 'create')")
    ec2_parser.add_argument("--instance-id", help="Instance ID (required for 'start', 'stop', 'terminate')")
    ec2_parser.add_argument("--vpc-id", help="VPC ID (optional, defaults to the default VPC if not provided)")
    ec2_parser.add_argument("--subnet-id", help="Subnet ID (optional, defaults to an available subnet in the VPC if not provided)")
    ec2_parser.add_argument("--public", action="store_true", help="Assign a public IPv4 address to the instance")
    ec2_parser.add_argument("--private", action="store_true", help="Do NOT assign a public IPv4 address to the instance")
    ec2_parser.add_argument("--keypair", help="SSH key pair name for the EC2 instance")

    # S3 subcommands
    s3_parser = subparsers.add_parser("s3", help="Manage S3 buckets")
    s3_parser.add_argument("action", choices=["create", "upload", "list", "delete"], help="Action to perform", nargs="?")
    s3_parser.add_argument("--public", action="store_true", help="Make the bucket public (requires confirmation)")
    s3_parser.add_argument("--bucket-name", help="Bucket name (required for 'upload' and 'delete')")
    s3_parser.add_argument("--file-path", help="File path to upload (required for 'upload')")
    s3_parser.add_argument("--region", help="AWS region for the S3 bucket (default: us-east-1)")

    # Route53 subcommands
    route53_parser = subparsers.add_parser("route53", help="Manage Route53 DNS")
    route53_parser.add_argument("action", choices=["create-zone", "add-record", "list-zones", "delete"], help="Action to perform", nargs="?")
    route53_parser.add_argument("--zone-id", help="Hosted zone ID (required for 'add-record' and 'delete')")
    route53_parser.add_argument("--record-name", help="DNS record name (required for 'add-record')")
    route53_parser.add_argument("--record-type", choices=["A", "CNAME", "TXT"], help="Record type (required for 'add-record')")
    route53_parser.add_argument("--record-value", help="Record value (required for 'add-record')")
    route53_parser.add_argument("--vpc-id", help="VPC ID for private hosted zones (required for 'create-zone')")

    # All Resources Subcommands
    all_parser = subparsers.add_parser("all", help="Manage all CLI-created resources")
    all_parser.add_argument("action", choices=["terminate-all", "list-all"], help="Action to perform", nargs="?")

    try:
        parsed_args = parser.parse_args(args)

        if not parsed_args.resource:
            print(Fore.RED + "Error: You must specify a resource (ec2, s3, route53, all).")
            return

        if not parsed_args.action:
            print(Fore.RED + f"Error: You must specify an action for {parsed_args.resource}.")
            return

        # EC2
        if parsed_args.resource == "ec2":
            if parsed_args.action == "create":
                if not parsed_args.instance_type or not parsed_args.ami:
                    print(Fore.RED + "Error: --instance-type and --ami are required for creating an EC2 instance.")
                else:
                    assign_public_ip = True if parsed_args.public else False
                    instance_details = ec2_manager.create_instance(
                        parsed_args.instance_type,
                        parsed_args.ami,
                        parsed_args.vpc_id,
                        parsed_args.subnet_id,
                        assign_public_ip,
                        parsed_args.keypair,
                    )

                    if instance_details:
                        print(Fore.GREEN + "\n=== EC2 Instance Created ===")
                        print(Fore.GREEN + f"Instance ID   : {instance_details['instance_id']}")
                        print(Fore.GREEN + f"Instance Type : {instance_details['instance_type']}")
                        print(Fore.GREEN + f"AMI ID        : {instance_details['ami_id']}")
                        print(Fore.GREEN + f"VPC Name      : {instance_details['vpc_name']} ({instance_details['vpc_id']})")
                        print(Fore.GREEN + f"Subnet Name   : {instance_details['subnet_name']} ({instance_details['subnet_id']})")
                        print(Fore.GREEN + f"Public IP     : {instance_details['public_ip']}")
                        print(Fore.GREEN + f"Key Pair Name : {instance_details['keypair_name']}")
                        print(Fore.GREEN + "============================")


            elif parsed_args.action == "list":
                ec2_manager.list_instances()
            elif parsed_args.action == "start":
                ec2_manager.start_instance(parsed_args.instance_id)
            elif parsed_args.action == "stop":
                ec2_manager.stop_instance(parsed_args.instance_id)
            elif parsed_args.action == "terminate":
                ec2_manager.terminate_instance(parsed_args.instance_id)

        # s3
        elif parsed_args.resource == "s3":
            if parsed_args.action == "create":
                region = parsed_args.region if parsed_args.region else "us-east-1"
                s3_manager.create_bucket(parsed_args.public, region)

            elif parsed_args.action == "list":
                s3_manager.list_buckets()
            elif parsed_args.action == "upload":
                s3_manager.upload_file(parsed_args.bucket_name, parsed_args.file_path)
            elif parsed_args.action == "delete":
                s3_manager.delete_bucket(parsed_args.bucket_name)

        # route53
        elif parsed_args.resource == "route53":
            if parsed_args.action == "create-zone":
                if not parsed_args.vpc_id:
                    print(Fore.RED + "Error: --vpc-id is required to create a private hosted zone.")
                else:
                    route53_manager.create_hosted_zone(parsed_args.vpc_id)

            elif parsed_args.action == "list-zones":
                route53_manager.list_zones()
            elif parsed_args.action == "add-record":
                route53_manager.add_dns_record(parsed_args.zone_id, parsed_args.record_name, parsed_args.record_type, parsed_args.record_value)
            elif parsed_args.action == "delete":
                route53_manager.delete_hosted_zone(parsed_args.zone_id)

        # all
        elif parsed_args.resource == "all":
            if parsed_args.action == "list-all":
                list_all_resources()
            elif parsed_args.action == "terminate-all":
                terminate_all_resources()

    except SystemExit:
        pass 

if __name__ == "__main__":
    main()


