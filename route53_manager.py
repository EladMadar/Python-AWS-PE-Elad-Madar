import boto3
import utils
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

route53_client = boto3.client("route53")

def create_hosted_zone(vpc_id, domain_name=None):
    """
    Creates a Route 53 private hosted zone with an optional custom domain name.

    Parameters:
        vpc_id (str): The VPC ID to associate with the hosted zone.
        domain_name (str, optional): The domain name (defaults to <aws-username>.com).
    """
    aws_username = utils.get_aws_username()
    domain_name = domain_name if domain_name else f"{aws_username}.com"

    response = route53_client.create_hosted_zone(
        Name=domain_name,
        VPC={"VPCRegion": "us-east-1", "VPCId": vpc_id},  
        CallerReference=str(hash(domain_name)),
    )

    zone_id = response["HostedZone"]["Id"]
    print(Fore.GREEN + f"Route 53 Hosted Zone Created: {domain_name} (ID: {zone_id}, VPC: {vpc_id})")

def add_dns_record(zone_id, record_name, record_type, record_value):
    """
    Adds a DNS record to a hosted zone.

    Parameters:
        zone_id (str): Hosted Zone ID.
        record_name (str): Name of the DNS record.
        record_type (str): Type of record (A, CNAME, TXT).
        record_value (str): Value of the record (e.g., an IP address or domain).
    """
    try:
        response = route53_client.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch={
                "Changes": [{
                    "Action": "UPSERT",
                    "ResourceRecordSet": {
                        "Name": record_name,
                        "Type": record_type,
                        "TTL": 300,
                        "ResourceRecords": [{"Value": record_value}]
                    }
                }]
            }
        )
        print(Fore.GREEN + f"DNS Record Created: {record_name} → {record_value} (Type: {record_type})")
    except Exception as e:
        print(Fore.RED + f"Error adding DNS record: {e}")


def list_zones():
    """
    Lists all hosted zones created by the CLI.

    Returns:
        list: A list of hosted zone IDs.
    """
    aws_username = utils.get_aws_username()
    response = route53_client.list_hosted_zones()
    cli_zones = [
        {"ID": zone["Id"], "Name": zone["Name"]}
        for zone in response["HostedZones"]
        if zone["Name"].startswith(f"{aws_username}")
    ]

    if cli_zones:
        print(Fore.CYAN + "Hosted Zones created by CLI:")
        for zone in cli_zones:
            print(Fore.CYAN + f"  - ID: {zone['ID']}, Name: {zone['Name']}")
    else:
        print(Fore.RED + "No hosted zones found.")

    return [zone["ID"] for zone in cli_zones]


def delete_hosted_zone(zone_id):
    """
    Deletes a Route 53 hosted zone after user confirmation.

    Parameters:
        zone_id (str): Hosted Zone ID.
    """
    confirm = input(Fore.MAGENTA + f"Are you sure you want to delete Route 53 hosted zone {zone_id}? (yes/no): ").strip().lower()
    if confirm == "yes":
        try:
            # Delete all DNS records before deleting the hosted zone
            records = route53_client.list_resource_record_sets(HostedZoneId=zone_id)
            for record in records["ResourceRecordSets"]:
                if record["Type"] not in ["NS", "SOA"]:
                    route53_client.change_resource_record_sets(
                        HostedZoneId=zone_id,
                        ChangeBatch={"Changes": [{"Action": "DELETE", "ResourceRecordSet": record}]}
                    )
            # Delete the hosted zone
            route53_client.delete_hosted_zone(Id=zone_id)
            print(Fore.GREEN + f"Route 53 hosted zone {zone_id} has been deleted.")
        except Exception as e:
            print(Fore.RED + f"Error deleting hosted zone: {e}")
    else:
        print(Fore.RED + "Operation canceled.")