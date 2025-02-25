import boto3
import utils
import colorama
from colorama import Fore

colorama.init(autoreset=True)

ec2_client = boto3.client("ec2")

def get_running_instances_count():
    """
    Counts the number of running EC2 instances created by the current AWS user.

    Returns:
        int: Number of running EC2 instances.
    """
    aws_username = utils.get_aws_username()

    response = ec2_client.describe_instances(
        Filters=[
            {"Name": "tag:Owner", "Values": [aws_username]},
            {"Name": "instance-state-name", "Values": ["pending", "running"]}
        ]
    )

    return sum(len(reservation["Instances"]) for reservation in response["Reservations"])

def create_instance(instance_type, os_name, vpc_id=None, subnet_id=None, assign_public_ip=True, keypair_name=None):
    """
    Creates an EC2 instance with an optional public IP and SSH key pair.

    Parameters:
        instance_type (str): EC2 instance type (t3.nano or t4g.nano).
        os_name (str): OS type (ubuntu or amazon-linux).
        vpc_id (str, optional): The VPC where the instance should be created.
        subnet_id (str, optional): The specific subnet for the instance (if provided, overrides auto-selection).
        assign_public_ip (bool): Whether to assign a public IPv4 address (default: True).
        keypair_name (str, optional): The SSH key pair to use for the instance.

    Returns:
        dict: Details of the created EC2 instance.
    """
    aws_username = utils.get_aws_username()

    # Check instance limit
    if get_running_instances_count() >= 2:
        print(Fore.RED + f"Error: You already have 2 running instances. No more instances can be created.")
        return None

    instance_name = utils.generate_resource_name("ec2")
    ami_id = utils.get_latest_ami(os_name, instance_type)

    if not ami_id:
        print(Fore.RED + "Failed to retrieve the correct AMI. Aborting instance creation.")
        return None

    # Determine the VPC ID if not provided
    if not vpc_id:
        vpcs = ec2_client.describe_vpcs(Filters=[{"Name": "is-default", "Values": ["true"]}])["Vpcs"]
        if vpcs:
            vpc_id = vpcs[0]["VpcId"]
            print(f"Using default VPC: {vpc_id}")
        else:
            print(Fore.RED + "No default VPC found. Specify --vpc-id.")
            return None

    # Determine the subnet ID if not provided
    if not subnet_id:
        subnets = ec2_client.describe_subnets(Filters=[{"Name": "vpc-id", "Values": [vpc_id]}])["Subnets"]

        available_subnet = None
        for subnet in subnets:
            if subnet["AvailableIpAddressCount"] > 0:
                available_subnet = subnet
                break

        if available_subnet:
            subnet_id = available_subnet["SubnetId"]
            subnet_name = next((tag["Value"] for tag in available_subnet.get("Tags", []) if tag["Key"] == "Name"), "Unnamed Subnet")
            print(Fore.GREEN + f"Using available subnet: {subnet_id} ({subnet_name})")
        else:
            print(Fore.RED + "No available subnets found in the specified VPC.")
            return None
    else:
        subnet_info = ec2_client.describe_subnets(SubnetIds=[subnet_id])["Subnets"][0]
        subnet_name = next((tag["Value"] for tag in subnet_info.get("Tags", []) if tag["Key"] == "Name"), "Unnamed Subnet")

    vpc_info = ec2_client.describe_vpcs(VpcIds=[vpc_id])["Vpcs"][0]
    vpc_name = next((tag["Value"] for tag in vpc_info.get("Tags", []) if tag["Key"] == "Name"), "Unnamed VPC")

    response = ec2_client.run_instances(
        ImageId=ami_id,
        InstanceType=instance_type,
        MinCount=1,
        MaxCount=1,
        KeyName=keypair_name if keypair_name else None,
        TagSpecifications=[{
            "ResourceType": "instance",
            "Tags": [
                {"Key": "Name", "Value": instance_name},
                {"Key": "Owner", "Value": aws_username},
                {"Key": "CreatedBy", "Value": "elad-madar-CLI"},
            ]
        }],
        NetworkInterfaces=[{
            "DeviceIndex": 0,
            "SubnetId": subnet_id,
            "AssociatePublicIpAddress": assign_public_ip,
            "Groups": []
        }]
    )

    instance_id = response["Instances"][0]["InstanceId"]

    # Retrieve public IP
    instance_description = ec2_client.describe_instances(InstanceIds=[instance_id])
    public_ip = instance_description["Reservations"][0]["Instances"][0].get("PublicIpAddress", "No Public IP Assigned")

    # Print EC2 Instance Details
    # print(Fore.GREEN + "\n=== EC2 Instance Created ===")
    # print(Fore.GREEN + f"Instance ID   : {instance_id}")
    # print(Fore.GREEN + f"Instance Type : {instance_type}")
    # print(Fore.GREEN + f"AMI ID        : {ami_id}")
    # print(Fore.GREEN + f"VPC Name      : {vpc_name} ({vpc_id})")
    # print(Fore.GREEN + f"Subnet Name   : {subnet_name} ({subnet_id})")
    # print(Fore.GREEN + f"Public IP     : {public_ip}")
    # print(Fore.GREEN + f"Key Pair Name : {keypair_name if keypair_name else 'None'}")
    # print(Fore.GREEN + "============================")

    return {
        "instance_id": instance_id,
        "instance_type": instance_type,
        "ami_id": ami_id,
        "vpc_id": vpc_id,
        "vpc_name": vpc_name,
        "subnet_id": subnet_id,
        "subnet_name": subnet_name,
        "public_ip": public_ip,
        "keypair_name": keypair_name if keypair_name else "None"
    }

def list_instances():
    """
    Lists all EC2 instances created via the CLI.
    """
    response = ec2_client.describe_instances(Filters=[{"Name": "tag:CreatedBy", "Values": ["elad-madar-CLI"]}])

    instances = []
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instances.append({
                "InstanceId": instance["InstanceId"],
                "State": instance["State"]["Name"],
                "Type": instance["InstanceType"],
                "AMI": instance["ImageId"],
                "Name": next((tag["Value"] for tag in instance.get("Tags", []) if tag["Key"] == "Name"), "Unknown"),
            })

    if instances:
        for instance in instances:
            print(Fore.CYAN + f"Instance ID: {instance['InstanceId']}, State: {instance['State']}, Type: {instance['Type']}, AMI: {instance['AMI']}, Name: {instance['Name']}")
    else:
        print(Fore.MAGENTA + "No EC2 instances found.")

    return instances

def start_instance(instance_id):
    """
    Starts an EC2 instance by its Instance ID.
    """
    try:
        response = ec2_client.start_instances(InstanceIds=[instance_id])
        current_state = response["StartingInstances"][0]["CurrentState"]["Name"]
        print(Fore.GREEN + f"Instance {instance_id} is now {current_state}.")
    except Exception as e:
        print(Fore.RED + f"Error starting instance {instance_id}: {e}")

def stop_instance(instance_id):
    """
    Stops an EC2 instance by its Instance ID.
    """
    try:
        response = ec2_client.stop_instances(InstanceIds=[instance_id])
        current_state = response["StoppingInstances"][0]["CurrentState"]["Name"]
        print(Fore.GREEN + f"Instance {instance_id} is now {current_state}.")
    except Exception as e:
        print(Fore.RED + f"Error stopping instance {instance_id}: {e}")

def terminate_instance(instance_id):
    """
    Terminates an EC2 instance after user confirmation.
    """
    confirm = input(f"Are you sure you want to terminate EC2 instance {instance_id}? (yes/no): ").strip().lower()
    if confirm == "yes":
        ec2_client.terminate_instances(InstanceIds=[instance_id])
        print(Fore.GREEN + f"EC2 instance {instance_id} has been terminated.")
    else:
        print(Fore.RED + "Operation canceled.")