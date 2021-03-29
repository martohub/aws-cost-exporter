# Prometheus AWS Cost Exporter


1. implemented second API call for fetching both blended/unblended metric  
2. implemented API call to STS to fetch account number and have it in the metrics  

to do: hopefully, implement assume role functionality with Alex Shamara & Lil Polly

#login with aws configure, pip3 install boto3 prometheus_client  
git clone https://github.com/martohub/aws-cost-exporter && cd aws-cost-exporter  
export TAG_PROJECT='environment' && ./aws-cost-exporter.py 
 
http://localhost:9050  

```
# HELP aws_monthly_blended_cost in USD by tag
# TYPE aws_monthly_blended_cost gauge
aws_monthly_blended_cost{account_number="111111111111",environment="not_defined_by_the_tag"} 2.75
aws_monthly_blended_cost{account_number="111111111111",environment="dev"} 8.35
aws_monthly_blended_cost{account_number="111111111111",environment="qa"} 3.17
aws_monthly_blended_cost{account_number="111111111111",environment="test"} 5.48
# HELP aws_monthly_unblended_cost in USD by tag
# TYPE aws_monthly_unblended_cost gauge
aws_monthly_unblended_cost{account_number="111111111111",environment="not_defined_by_the_tag"} 2.75
aws_monthly_unblended_cost{account_number="111111111111",environment="dev"} 8.35
aws_monthly_unblended_cost{account_number="111111111111",environment="qa"} 3.17
aws_monthly_unblended_cost{account_number="111111111111",environment="test"} 5.48
```

# API string debugging

python shell:

```
import time
import os
import re
import boto3
import datetime
now = datetime.datetime.utcnow()
end = datetime.datetime(year=now.year, month=now.month, day=now.day)
start = end - datetime.timedelta(days=30)
start = start.strftime('%Y-%m-%d')
end = end.strftime('%Y-%m-%d')
tagProject = 'application_id'
client = boto3.client('ce')
client.get_cost_and_usage(
	TimePeriod={
		'Start': start,
		'End':  end
	},
	Granularity='MONTHLY',
	Metrics=['UnblendedCost'],
	GroupBy=[
		{
			'Type': 'TAG',
			'Key': tagProject 
		},
	]
)
```

# Description

This exporter will query AWS Cost Explorer API search by a specific tag. This is useful for know the cost of a specific project. All you need to do is run it with the env variables. The script will discover and return the amount for each value founded on a specified tag.


# Authentication

The script uses boto, so, if you already have aws/credentials file, the script will work fine. You can use env variables also:

|Variable|Description|Default value|
|--------|-----------|-------------|
|PORT|Port for exporter listener| 9150|
|TAG_PROJECT|Tag to search|environment|
|AWS_DEFAULT_REGION| Your AWS REGION|-|
|AWS_ACCESS_KEY_ID|Your AWS Key|-|
|AWS_SECRET_ACCESS_KEY|Your AWS SECRET KEY|-|

# Usage

./aws-cost-exporter.py

# Docker

docker run --restart always -d -p 9150:9150 -e TAG_PROJECT="YOUR_TAG_PROJECT" -e AWS_DEFAULT_REGION="XXXX" -e AWS_ACCESS_KEY_ID="XXXXXX" -e AWS_SECRET_ACCESS_KEY="XXXXX" alanwds/aws-cost-exporter:latest

# Prometheus config

```
- job_name: aws-cost-exporter
  scrape_interval: 3600s
  scrape_timeout: 300s
  static_configs:
  - targets:
    - localhost:9150
```

# AWS IAM Policy
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ce:*"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
```

######

PR, comments, and enhancements are always welcome
