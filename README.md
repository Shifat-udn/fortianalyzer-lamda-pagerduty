# Fortianalyzer-lamda-pagerduty
FortiGate Policy Traffic Monitoring &amp; Automated Alerting

This project demonstrates an automated network security monitoring and incident alerting solution that integrates Fortinet, Python, and AWS serverless services. A FortiAnalyzer collects traffic logs from FortiGate firewalls within a private network, while an AWS Lambda function written in Python periodically connects to the FortiAnalyzer JSON-RPC API to analyze traffic for a specific FortiGate security policy over a defined time window. The Lambda function is triggered automatically every 10 minutes using Amazon EventBridge. If no traffic is detected for the monitored policy during the previous 10-minute period, Lambda publishes an alarm event to an Amazon SNS topic, which forwards the alert to PagerDuty for incident management and operational notification. The project demonstrates practical skills across network security, FortiGate firewall administration, FortiAnalyzer logging and API integration, Python automation, AWS Lambda, EventBridge, SNS, IAM, and PagerDuty, combining on-premises security infrastructure with cloud-based serverless automation to create a proactive policy monitoring and alerting workflow.

<img width="922" height="713" alt="fortianalyzer-lamda-pagerduty (1)" src="https://github.com/user-attachments/assets/0a47dd8f-d010-4847-b74b-7f1a04179af0" />

Environment 
- Fotianalyzer 7.6.7 
- Fortigate 7.6.6
- Python Runtime 3.12

## Fortianalyzer User with API Access:
On Fotianalyzer create a local read-only user with JSON api access 
<img width="731" height="586" alt="image" src="https://github.com/user-attachments/assets/506a547a-855f-4044-a9dd-55c35a0c692c" />

## Lamda function :

log in to the AWS Management Console, navigate to the Lambda service, click Create function, choose Author from scratch, enter a function name, select Python 3.14 from the Runtime drop-down menu, and click Create function. (Make sure the function can reach Fotianalyzer. VPC and subnet configuration might be needed)

Once created, switch to the Configuration tab in your function's overview, select Environment variables from the side menu, click Edit, 
add 
- DEV_NAME (Name of the Forigate showing in the Analyzer log)
- FAZ_HOST (FortiAnalyzer IP)
- FAZ_PASSWORD ( Fotianalyzer local user password)
- FAZ_USER (Fotianalyzer local username)
- MONITOR_TIME_MIN (Observation Time)
- POLICY_ID (Policy ID of monitoring policy)
- SNS_TOPIC (arn of SNS topic , where alert goes)
- 
## AWS SNS & Pagerduty Integrations :
Crate a standard SNS topic and add a HTTPS subscription. 
<img width="1491" height="467" alt="image" src="https://github.com/user-attachments/assets/a156507c-806a-44ba-a837-a0243666e2d1" />
On the PagerDuty side Create Servcie and add CloudWatch Intrigration If you need take help from : https://support.pagerduty.com/main/docs/amazon-cloudwatch-integration-guide 
<img width="840" height="402" alt="image" src="https://github.com/user-attachments/assets/23f9060c-4c95-43dc-b96f-f710f0d7f6a9" />

Fortianalyzer API referance : 
https://how-to-fortianalyzer-api.readthedocs.io/en/latest/docs/pilot/logview-search.html
