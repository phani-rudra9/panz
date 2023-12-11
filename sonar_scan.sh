#!/bin/bash
curl -u admin:phani  http://3.101.129.2:9000//api/qualitygates/project_status?projectKey=demo > demo.json
sonar_scan=$(cat demo.json | grep -i status | cut -d ':' -f 3 | cut -d ',' -f 1 | tr -d '"')
if [[ sonar_scan -eq ok ]]
then
    echo "sonar_scan_status is $sonar_scan and it's safe"
else
    echo "sonar_scan_status is having errors and please check"
    exit 1
fi
