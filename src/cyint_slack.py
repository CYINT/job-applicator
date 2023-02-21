import requests 
import os
import json
from dotenv import load_dotenv
load_dotenv()
def talk_to_slack(message):
    webhook = os.environ["MARKETING_SLACK_WEBHOOK"]
    payload = { "text" : message }
    return requests.post(webhook, json.dumps(payload))

