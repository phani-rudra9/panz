#!/bin/bash
SERVICE="demo"
CLUSTER_NAME="sample"
AWS_REGION="us-east-2"
# export AWS_PROFILE=default

# Register a new Task definition 
aws ecs register-task-definition --family demo8am-task-def --cli-input-json file://task-new.json --region $AWS_REGION

# Update Service in the Cluster
aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE --task-definition demo8am-task-def --desired-count 1 --region $AWS_REGION

