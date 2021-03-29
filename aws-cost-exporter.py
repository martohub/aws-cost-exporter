#!/usr/bin/env python3

from prometheus_client import start_http_server, Metric, REGISTRY
import time
import os
import re
import boto3
import datetime
#Try get the TAG_PROJECT env variable. If not defined, we will use the Scost
tagProject = os.getenv('TAG_PROJECT','environment')
#tagProject1 = os.getenv('TAG_PROJECT','application_id')


#Try get the PORT env variable. If not defined, we will use the 9150 
port = os.getenv('PORT',9150)

def getCosts():


	#Create a boto3 connection with cost explorer
	client = boto3.client('ce')

	#Get the current time
	now = datetime.datetime.utcnow()

	# Set the end of the range to start of the current day 
	end = datetime.datetime(year=now.year, month=now.month, day=now.day)

	# Subtract a day to define the start of the range 
	start = end - datetime.timedelta(days=30)

	# Convert them to strings
	start = start.strftime('%Y-%m-%d')
	end = end.strftime('%Y-%m-%d')

	print("Starting script searching by the follow time range")
	print(start + " - " + end)

	#Call AWS API to get costs
	response = client.get_cost_and_usage(
		TimePeriod={
			'Start': start,
			'End':  end
		},
		Granularity='MONTHLY',
		Metrics=['BlendedCost'],
		GroupBy=[
			{
				'Type': 'TAG',
				'Key': tagProject 
			},
		]
	)
	#Create an empty dictionary
	projectValues = {}


#nov api kol i biblioteka za unblended
	response1 = client.get_cost_and_usage(
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
	projectValues1 = {}


	#Run the response and make a dictionary with tag name and tag value
	for project in response["ResultsByTime"][0]["Groups"]:

		#Search for tag
		namestring = project['Keys'][0]
		name = re.search("\$(.*)", namestring).group(1)

		#If name is none, let's defined it as Other
		if name is None or name == "":
			name = "not_defined_by_the_tag"

		#Get the value
		amount = project['Metrics']['BlendedCost']['Amount']
		#Format the time to 0.2 points
		amount = "{0:.2f}".format(float(amount))

		#Append the values in the directionary
		projectValues[name] = float(amount)
	#Return the dictionary with all those values
	return projectValues



#zavurti go pak, hvani s regex i vurni valueto v novata biblioteka

	for project1 in response1["ResultsByTime"][0]["Groups"]:
		namestring1 = project1['Keys'][0]
		name1 = re.search("\$(.*)", namestring1).group(1)
		if name1 is None or name1 == "":
			name1 = "not_defined_by_the_tag1"
		amount1 = project1['Metrics']['BlendedCost']['Amount']
		amount1 = "{0:.2f}".format(float(amount1))
		projectValues1[name] = float(amount1)
	return projectValues1




#Start classe collector
class costExporter(object):

	def collect(self):

		#Expose the metric
		#Create header
		metric = Metric('aws_monthly_blended_cost','in USD by tag','gauge')
		#Run the retuned dictionary and expose the metrics
		
		#nov API call kum sts-a za da vzema account nomera
		account_number = boto3.client('sts').get_caller_identity().get('Account')

		for project,cost in getCosts().items():
			metric.add_sample('aws_monthly_blended_cost',value=cost,labels={'account_number':account_number,tagProject:project})
		#/Expose the metric
		yield metric

		###zapishi i novata biblioteka
		metric1 = Metric('aws_monthly_unblended_cost','in USD by tag','gauge')
		for project1,cost1 in getCosts().items():
			metric1.add_sample('aws_monthly_unblended_cost',value=cost1,labels={'account_number':account_number,tagProject:project1})
		yield metric1

if __name__ == '__main__':

	start_http_server(port)
	metrics = costExporter()
	REGISTRY.register(metrics)
	while True: time.sleep(1) 
