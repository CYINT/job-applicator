import boto3
import os
import math
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv
load_dotenv()

def initiate_dynamo_resource():
    AWS_ACCESS_KEY = os.environ["AWS_ACCESS_KEY"]
    AWS_SECRET_KEY = os.environ["AWS_SECRET_KEY"]
    AWS_REGION = os.environ["AWS_REGION"]
    return boto3.resource(
        "dynamodb",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )

def insert_records(resource, records):
    DYNAMO_TABLE = os.environ["DYNAMO_DB_TABLE"]
    responses = []
    table = resource.Table(DYNAMO_TABLE)
    
    batches = math.ceil(len(records) / 50)
    
    for batch in range(batches):
        recordset = records[batch*50:50+(batch*50)]
        for record in recordset:
            responses.append(
                table.put_item(Item=record)
            )
    
    return responses

def get_items(resource, keys):
    DYNAMO_TABLE = os.environ["DYNAMO_DB_TABLE"]
    table = resource.Table(DYNAMO_TABLE)
    output = {}

    
    batches = math.ceil(len(keys) / 50)
    
    for batch in range(batches):
        keyset = keys[batch*50:50+(batch*50)]
        GetKeys = {
            table.name:  {
                "Keys": [{ "job_id": id } for id in keyset]
            }
        }
        
        response = resource.batch_get_item(RequestItems=GetKeys)
        for item in response["Responses"][table.name]:
            output[item["job_id"]] = item
        
    return output

def get_unprocessed_opportunities(resource):
    DYNAMO_TABLE = os.environ["DYNAMO_DB_TABLE"]
    table = resource.Table(DYNAMO_TABLE)
    output = {}
    response = table.query(
        KeyConditionExpression=Key('jira').eq(0),
        IndexName="jira-index"
    )
    
    for item in response["Items"]:
       output[item["job_id"]] = item

    return output
