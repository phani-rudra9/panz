import boto3
import json
import os
import sys

def main():
    # Read branch name and instance ID from script arguments
    branch_name = sys.argv[1]
    instance_id = sys.argv[2]

    # Retrieve environment variables
    alb_arn = os.getenv('ALB_ARN')
    alb_dns = os.getenv('ALB_DNS')
    hosted_zone_id = os.getenv('HOSTED_ZONE_ID')
    region = os.getenv('AWS_REGION', 'us-east-2')

    dns_name = f"planos{branch_name[:10]}.ecgtest.link"

    # Initialize AWS clients
    elb_client = boto3.client('elbv2', region_name=region)
    route53_client = boto3.client('route53', region_name=region)

    # Step 1: Check if Route 53 record already exists
    print(f"Checking for existing Route 53 record: {dns_name}")
    try:
        response = route53_client.list_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            StartRecordName=dns_name,
            MaxItems="1"
        )
        if response['ResourceRecordSets'] and response['ResourceRecordSets'][0]['Name'] == f"{dns_name}.":
            print("Route 53 record already exists. Skipping creation.")
            return
    except Exception as e:
        print(f"Error checking Route 53 record: {e}")

    # Step 2: Check if Target Group exists
    print(f"Checking for existing Target Group: {branch_name[:10]}-tg")
    try:
        tg_response = elb_client.describe_target_groups(
            Names=[f"{branch_name[:10]}-tg"]
        )
        target_group_arn = tg_response['TargetGroups'][0]['TargetGroupArn']
        print(f"Target Group already exists: {target_group_arn}. Skipping creation.")
    except elb_client.exceptions.TargetGroupNotFoundException:
        print("Target Group not found. Proceeding to create.")
        try:
            tg_response = elb_client.create_target_group(
                Name=f"{branch_name[:10]}-tg",
                Protocol='HTTP',
                Port=6543,
                VpcId="YOUR_VPC_ID",
                HealthCheckPath='/health',
                TargetType='instance'
            )
            target_group_arn = tg_response['TargetGroups'][0]['TargetGroupArn']
            print(f"Created Target Group: {target_group_arn}")
        except Exception as e:
            print(f"Error creating Target Group: {e}")
            return

    # Step 3: Register EC2 instance to Target Group
    print(f"Registering instance {instance_id} to Target Group.")
    try:
        elb_client.register_targets(
            TargetGroupArn=target_group_arn,
            Targets=[{'Id': instance_id, 'Port': 6543}]
        )
        print(f"Registered instance {instance_id} with Target Group {target_group_arn}.")
    except Exception as e:
        print(f"Error registering targets: {e}")
        return

    # Step 4: Create Listener Rules for ALB
    print("Creating Listener Rules.")
    try:
        # HTTP Listener Rule
        elb_client.create_rule(
            ListenerArn="YOUR_HTTP_LISTENER_ARN",
            Conditions=[{'Field': 'host-header', 'Values': [dns_name]}],
            Actions=[{'Type': 'redirect', 'RedirectConfig': {'Protocol': 'HTTPS', 'Port': '443', 'StatusCode': 'HTTP_301'}}],
            Priority=100
        )
        print("Created HTTP listener rule for redirect to HTTPS.")

        # HTTPS Listener Rule
        elb_client.create_rule(
            ListenerArn="YOUR_HTTPS_LISTENER_ARN",
            Conditions=[{'Field': 'host-header', 'Values': [dns_name]}],
            Actions=[{'Type': 'forward', 'TargetGroupArn': target_group_arn}],
            Priority=200
        )
        print("Created HTTPS listener rule to forward traffic.")
    except Exception as e:
        print(f"Error creating listener rules: {e}")

    # Step 5: Create or Update Route 53 DNS record
    print(f"Creating or updating Route 53 record for {dns_name}.")
    try:
        route53_client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                'Changes': [{
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': dns_name,
                        'Type': 'A',
                        'AliasTarget': {
                            'HostedZoneId': os.getenv('ALB_HOSTED_ZONE_ID'),
                            'DNSName': alb_dns,
                            'EvaluateTargetHealth': False
                        }
                    }
                }]
            }
        )
        print(f"Route 53 record created for {dns_name}.")
    except Exception as e:
        print(f"Error creating Route 53 record: {e}")

if __name__ == "__main__":
    main()
