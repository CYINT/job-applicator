from src.cyint_dynamodb import initiate_dynamo_resource, insert_records, get_items, get_unprocessed_opportunities
import random
import pytest

@pytest.fixture(scope='function')
def dynamodb_resource():
    client = initiate_dynamo_resource()
    return client

def test_insert_records(dynamodb_resource):
    records = [{
        "job_id": '123456',
        "title": 'Test Job',
        "company": 'Fake Company',
        "path": 'https://www.linkedin.com/some/fake/path2',
        "jira": 0
    },{
        "job_id": '7890123',
        "title": 'Test Job 2',
        "company": 'Fake Company 2',
        "path": 'https://www.linkedin.com/some/fake/path2',
        "jira": 0
    }]
    responses = insert_records(dynamodb_resource, records)
    for response in responses:
        assert response['ResponseMetadata']['HTTPStatusCode'] == 200

def test_get_items(dynamodb_resource):

    items = ['123456', '7890123']
    for i in range(200):
        items.append(str(random.randint(100000,600000)))

    items = get_items(dynamodb_resource, items)
    assert ('123456' in items.keys() and '7890123' in items.keys())

def test_get_unprocessed_opportunities(dynamodb_resource):
    items = get_unprocessed_opportunities(dynamodb_resource)
    assert len(items) > 1
    for key in items:
        assert items[key]['jira'] == 0