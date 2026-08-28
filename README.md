# Fortianalyzer-lamda-pagerduty
FortiGate Policy Traffic Monitoring &amp; Automated Alerting

This project demonstrates an automated network security monitoring and incident alerting solution that integrates Fortinet, Python, and AWS serverless services. A FortiAnalyzer collects traffic logs from FortiGate firewalls within a private network, while an AWS Lambda function written in Python periodically connects to the FortiAnalyzer JSON-RPC API to analyze traffic for a specific FortiGate security policy over a defined time window. The Lambda function is triggered automatically every 10 minutes using Amazon EventBridge. If no traffic is detected for the monitored policy during the previous 10-minute period, Lambda publishes an alarm event to an Amazon SNS topic, which forwards the alert to PagerDuty for incident management and operational notification. The project demonstrates practical skills across network security, FortiGate firewall administration, FortiAnalyzer logging and API integration, Python automation, AWS Lambda, EventBridge, SNS, IAM, and PagerDuty, combining on-premises security infrastructure with cloud-based serverless automation to create a proactive policy monitoring and alerting workflow.

                    ORGANIZATION NETWORK
                           │
                           │ Traffic
                           ▼
                    ┌──────────────┐
                    │   FortiGate  │
                    │   Firewall   │
                    └──────┬───────┘
                           │
                           │ Traffic Logs
                           ▼
                    ┌──────────────┐
                    │ FortiAnalyzer │
                    │   Private    │
                    │   Network    │
                    └──────┬───────┘
                           │
                    FortiAnalyzer API
                           │
                           │ HTTPS / JSON-RPC
                           ▼
                 ┌────────────────────┐
                 │    AWS Lambda      │
                 │ Python Automation   │
                 └─────────┬──────────┘
                           │
                  Policy traffic check
                           │
                    No traffic for 10m?
                       ┌────┴────┐
                      YES        NO
                       │          │
                       ▼          ▼
                ┌───────────┐   Normal
                │    SNS    │   operation
                │   Topic   │
                └─────┬─────┘
                      │
                      │
                      ▼
                ┌────────────┐
                │ PagerDuty  │
                │ Incident   │
                └────────────┘
