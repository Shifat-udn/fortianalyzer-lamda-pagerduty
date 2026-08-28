import json
import os
import boto3
import ssl
import requests
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

FAZ_TZ = ZoneInfo("America/New_York") # Timezone of fortianalyzer
FAZ_HOST = os.environ["FAZ_HOST"]
FAZ_USER = os.environ["FAZ_USER"]
FAZ_PASSWORD = os.environ["FAZ_PASSWORD"]
POLICY_ID = os.environ["POLICY_ID"]
SNS_TOPIC = os.environ["SNS_TOPIC"]
DEV_NAME = os.environ["DEV_NAME"] #DEVICE NAME of FORTIGATE where the policy resides
ADOM = "root"
TIME_NOW = now = datetime.now(timezone.utc).astimezone(FAZ_TZ)
AWS_ACCOUNT_ID = "111110011101" #AWS Account ID
ssl_context = ssl._create_unverified_context()

# login to FortiAnalyzer
def faz_login():

    url = f"https://{FAZ_HOST}/jsonrpc"

    payload = {
        "id":1,
        "method":"exec",
        "params":[
            {
                "url":"/sys/login/user",
                "data":{
                    "user":FAZ_USER,
                    "passwd":FAZ_PASSWORD
                }
            }
        ]
    }

    response=requests.post(
        url,
        json=payload,
        verify=False
    )

    result=response.json()

    print(json.dumps(result, indent=4)) 
    # will remove this debug print later

    return result["session"]

# logout from FortiAnalyzer

def faz_logout(session_id):

    url = f"https://{FAZ_HOST}/jsonrpc"

    payload = {
        "id":1,
        "method":"exec",
        "params":[
            {
                "url":"/sys/logout"
            }
        ],
	    "session": session_id
    }

    response=requests.post(
        url,
        json=payload,
        verify=False
    )

    result=response.json()

    
    return result
# logout from FortiAnalyzer
def get_taskid(session):
    # Lambda's clock is always UTC; convert to FortiAnalyzer's local (EST/EDT) time
    now = TIME_NOW

    ten_minutes_ago = now - timedelta(minutes=10)
    time_range = {
                            "start" : ten_minutes_ago.strftime("%Y-%m-%d %H:%M:%S"),
                            "end" : now.strftime("%Y-%m-%d %H:%M:%S")
                        }
    filter_log = f"policyid=={POLICY_ID} and devname=='{DEV_NAME}'"                  
    payload = {
        "id": 1,
	    "jsonrpc": "2.0",
        "method": "add",
        "session": session ,
        "params": [
		
					{
					  "url": "/logview/adom/root/logsearch",
					  "apiver": 3,
					  "device": [
						{
						  "devid": "All_FortiGate"
						}
					  ],
					  "logtype": "traffic",
					  "filter": filter_log,
					  "time-order": "desc",
					  "time-range": time_range
					}
  
		          ]
    }


    response = requests.post(
        f"https://{FAZ_HOST}/jsonrpc",
        json=payload,
        verify=False
    )
    result_json = response.json()
    return result_json["result"]["tid"]

def get_log_count(session, task_id):
    text = "/logview/adom/root/logsearch/"
    api_url = f"{text}{task_id}"
    payload = {
        "id": 2,
	    "jsonrpc": "2.0",
        "method": "get",
        "session": session ,
        "params": [
		
					{
					  "url": api_url,
					  "apiver": 3,
					  "limit": 100,
                      "offset": 0
					}
  
		          ]
    }


    response = requests.post(
        f"https://{FAZ_HOST}/jsonrpc",
        json=payload,
        verify=False
    )
    result_json = response.json()
    return result_json["result"]["total-count"]




def send_alert():
    sns = boto3.client('sns', region_name='us-east-1')
    arn = f'{SNS_TOPIC}'
    now = TIME_NOW.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+0000"
    
    payload = {
        "AWSAccountId": AWS_ACCOUNT_ID,
        "AlarmActions": [
            arn
        ],
        "AlarmArn": "arn:aws:cloudwatch:us-east-1:111110010100:alarm:POLICY",
        "AlarmConfigurationUpdatedTimestamp": now,
        "AlarmDescription": "The policy X has no data flow for last 10 min ", # message for pagerduty
        "AlarmName": "Policy-not-hit",
        "InsufficientDataActions": [],
        "NewStateReason": "Data missing: AWS Frotigate policy Traffic Missing for 10min.",
        "NewStateValue": "ALARM",     # triggers the incident
        "OKActions": [],
        "OldStateValue": "OK",         # <-- critical: defines the OK -> ALARM transition
        "Region": "US East (N. Virginia)",
        "StateChangeTime": now,
        "Trigger": {
            "ComparisonOperator": "Data missing for 10m",  # <-- critical
            "DatapointsToAlarm": 1,
            "Dimensions": [
                {"name": "MetricName", "value": "CustomAppExecutionError"}
            ],
            "EvaluateLowSampleCountPercentile": "",
            "EvaluationPeriods": 1,
            "MetricName": "No data - Policy X- AWS",
            "Namespace": "AWS/Application",
            "Period": 300,
            "Statistic": "SUM",
            "StatisticType": "Statistic",
            "Threshold": 1.0,
            "TreatMissingData": "missing",
            "Unit": None
        }
    }
   


    response = sns.publish(
        TopicArn=arn,
        Subject="ALARM: Policy X Traffic Missing", # MUST start with ALARM
        Message=json.dumps(payload)
    )

    print("SNS Message ID:", response['MessageId'])



def lambda_handler(event, context):
    # get session id from log in
    session1 = faz_login()
    #get task id with session 
    taskid = get_taskid(session1)
    #wait 5sec so task can be completed
    time.sleep(5)
    # total policy hit in last 10 minuite
    total_policy_hit = get_log_count(session1, taskid)
    #logout after the task
    logout_session = faz_logout(session1)
    # triger SNS is no traffic for 10 min
    set_status = "No Alert !"
    #send_alert()
    if total_policy_hit == 0:
        set_status = "Alert !"
        send_alert()

    now = TIME_NOW
    # adjusting time differance
    ten_minutes_ago = datetime.fromtimestamp(now.timestamp() - 600, tz=timezone.utc)
    time_range = {
                            "start" : ten_minutes_ago.strftime("%Y-%m-%d %H:%M:%S"),
                            "end" : now.strftime("%Y-%m-%d %H:%M:%S")
                        }

    return {
        'statusCode': 200,
        'body': total_policy_hit,
        'time_range': time_range,
        'trigger': set_status
    }