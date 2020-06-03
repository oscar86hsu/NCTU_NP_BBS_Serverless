import json
import boto3
import os

client = boto3.client('dynamodb')


def lambda_handler(event, context):
    username = event['requestContext']['authorizer']['claims']['cognito:username']

    item = client.get_item(
        TableName=os.environ['USER_SUB_TABLE'],
        Key={'username': {'S': username}})

    if not "Item" in item:
        return {
            "statusCode": 200,
            "body": json.dumps("\n")
        }

    results = ""
    if "board" in item['Item']:
        results += "    Board:\n"
        for i in item['Item']['board']['L']:
            results += "        " + i['S'] + "\n"

    if "author" in item['Item']:
        results += "    Author:\n"
        for i in item['Item']['author']['L']:
            results += "        " + i['S'] + "\n"

    return {
        "statusCode": 200,
        "body": json.dumps(results)
    }

if __name__ == "__main__":
    event = {
        'requestContext':
        {
            'authorizer':
            {
                'claims':
                {
                    'cognito:username': 'aaa'
                }
            }
        }
    }
    os.environ['USER_SUB_TABLE'] = 'nctu-bbs-user-sub'
    print(json.dumps(lambda_handler(event, {})))
