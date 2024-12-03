import boto3
import os

def main():
    branch_name = os.getenv('BRANCH_NAME', 'feature/demo1')[:10]
    instance_id = os.getenv('INSTANCE_ID', 'i-0123456789abcdef0')
    hosted_zone_id = os.getenv('HOSTED_ZONE_ID')
    alb_dns = os.getenv('ALB_DNS')
    alb_arn = os.getenv('ALB_ARN')
    region = os.getenv('AWS_REGION', 'us-east-2')
    vpc_id = os.getenv('VPC_ID', 'vpc-123456')
    http_listener_arn = os.getenv('HTTP_LISTENER_ARN', 'listener-arn-http')
    https_listener_arn = os.getenv('HTTPS_LISTENER_ARN', 'listener-arn-https')

    dns_name = f"planos{branch_name}.ecgtest.link"

    elb_client = boto3.client('elbv2', region_name=region)
    route53_client = boto3.client('route53', region_name=region)

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

    try:
        tg_response = elb_client.create_target_group(
            Name=f"{branch_name}-tg",
            Protocol='HTTP',
            Port=6543,
            VpcId=vpc_id,
            HealthCheckPath='/health',
            TargetType='instance'
        )
        target_group_arn = tg_response['TargetGroups'][0]['TargetGroupArn']
    except elb_client.exceptions.TargetGroupNotFoundException:
        print("Target Group already exists. Skipping creation.")
        return

    elb_client.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=[{'Id': instance_id, 'Port': 6543}]
    )

    elb_client.create_rule(
        ListenerArn=http_listener_arn,
        Conditions=[{'Field': 'host-header', 'Values': [dns_name]}],
        Actions=[{'Type': 'redirect', 'RedirectConfig': {'Protocol': 'HTTPS', 'Port': '443', 'StatusCode': 'HTTP_301'}}],
        Priority=100
    )

    elb_client.create_rule(
        ListenerArn=https_listener_arn,
        Conditions=[{'Field': 'host-header', 'Values': [dns_name]}],
        Actions=[{'Type': 'forward', 'TargetGroupArn': target_group_arn}],
        Priority=200
    )

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

if __name__ == "__main__":
    main()
