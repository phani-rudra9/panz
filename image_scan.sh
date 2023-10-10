#!/bin/bash
repo_name="demo"
image_tag="SAMPLE-PROJECT-${BUILD_NUMBER}"
arn="arn:aws:sns:ap-south-1:351836203514:sample"

# Get image scan findings as JSON
image_scan_findings=$(aws ecr describe-image-scan-findings --repository-name "$repo_name" --image-id imageTag="$image_tag")

# Extract critical and high vulnerability counts using jq
critical_vulnr=$(echo "$image_scan_findings" | jq '.imageScanFindings.findingSeverityCounts."CRITICAL" // 0')
high_vulnr=$(echo "$image_scan_findings" | jq '.imageScanFindings.findingSeverityCounts."HIGH" // 0')

echo "High vulnerabilities: $high_vulnr"
echo "Critical vulnerabilities: $critical_vulnr"

if [[ $high_vulnr -gt 0 || $critical_vulnr -gt 0 ]]
then
    echo "Your image has high or critical vulnerabilities"
    aws sns publish --topic-arn "$arn" --message "Image vulnerabilities: High or critical vulnerabilities detected for image $image_tag in repository $repo_name" --subject "Image Vulnerability Alert"
    exit 1
else
    echo "Your image has no high or critical vulnerabilities"
fi
