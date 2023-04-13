from jira import JIRA
import os
import math
from time import sleep
from dotenv import load_dotenv
load_dotenv()

def authenticate_jira():
    JIRA_EMAIL = os.environ["JIRA_EMAIL"]
    JIRA_TOKEN = os.environ["JIRA_TOKEN"]
    JIRA_SERVER = os.environ["JIRA_SERVER"]
    JIRA_MARKETING_PROJECT = os.environ["JIRA_MARKETING_PROJECT"]
    jira = JIRA(
        options={ 'server': JIRA_SERVER },
        basic_auth=(JIRA_EMAIL, JIRA_TOKEN)
    )
    
    return jira

def create_opportunities(jira, jobs, project):
    batch_count = math.ceil(len(jobs)/50)
    issues = []
    for batch in range(batch_count):
        issue_list = [{  
            'project': {'key': project},
            'summary': f"{job['company']} - {job['title']}",
            "description": f"{job['company']} - {job['title']}",
            "issuetype": { "name": "Opportunity" },
            "customfield_10157": job['title'],
            "customfield_10158":  job['path'][:job["path"].index('?')],
            "customfield_10159": 0
        } for job in jobs[batch*50:50*(batch+1)]] 
        
        issues += jira.create_issues(field_list=issue_list)
        sleep(1)
    return issues

def get_new_opportunities(jira, start_at=0):
    issues = jira.search_issues(
        "project='MAR' AND issueType='Opportunity' and status='New Task'",
        startAt=start_at
    )

    return issues


def get_prepared_opportunities(jira, start_at=0):
    issues = jira.search_issues(
        "project='MAR' AND issueType='Opportunity' and status='Eligible for Application'",
        startAt=start_at
    )

    return issues