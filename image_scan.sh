#!/bin/bash
repo_name=demo
image_tag=demo-project-${BUILD_NUMBER}
arn="arn:aws:sns:us-east-2:971076122335:demo"
critical_vulnr=$(aws ecr describe-image-scan-findings --repository-name $repo_name --image-id imageTag=$image_tag --region us-east-2 | grep -i "findingSeverityCounts" -A 5 | grep -i critical | cut -d ":" -f 2 | tr -d ",")
high_vulnr=$(aws ecr describe-image-scan-findings --repository-name $repo_name --image-id imageTag=$image_tag --region us-east-2 | grep -i "findingSeverityCounts" -A 5 | grep -i high | cut -d ":" -f 2 | tr -d ",")

if [ -z "$critical_vulnr" ]; then
    critical_vulnr=0
fi

if [ -z "$high_vulnr" ]; then
    high_vulnr=0
fi

echo "High vulnerabilities: $high_vulnr"
echo "Critical vulnerabilities: $critical_vulnr"

if [[ $high_vulnr -gt 0 || $critical_vulnr -gt 0 ]]; then
   echo "Your image is having vulnerabilities, please check...."
   aws sns publish --topic-arn $arn --region us-east-2 --message "Your image in this $repo_name repo with image tag $image_tag has vulnerabilities, please check..."
   # exit 1
else
    echo "Your image is safe for deployment"
fi
