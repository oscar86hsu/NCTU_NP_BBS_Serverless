import json
import boto3
import os

client = boto3.client('dynamodb')


def lambda_handler(event, context):
    username = event['requestContext']['authorizer']['claims']['cognito:username']

    item = client.scan(
        TableName=os.environ['BOARD_SUB_TABLE'],
        FilterExpression="contains(#u, :a)",
        ExpressionAttributeNames={
            "#u": "user"
        },
        ExpressionAttributeValues={
            ":a": {"S": username}
        }
    )

    results = ""
    if item['Count'] > 0:
        results += "    Board:\n"
        for i in item['Items']:
            results += "        " + i['subscribe']['S'] + "\n"

    item = client.scan(
        TableName=os.environ['AUTHOR_SUB_TABLE'],
        FilterExpression="contains(#u, :a)",
        ExpressionAttributeNames={
            "#u": "user"
        },
        ExpressionAttributeValues={
            ":a": {"S": username}
        }
    )

    if item['Count'] > 0:
        results += "    Author:\n"
        for i in item['Items']:
            results += "        " + i['subscribe']['S'] + "\n"

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
                    'cognito:username': 'bbb'
                }
            }
        }
    }
    os.environ['BOARD_SUB_TABLE'] = 'nctu-bbs-board-sub'
    os.environ['AUTHOR_SUB_TABLE'] = 'nctu-bbs-author-sub'
    print(json.dumps(lambda_handler(event, {})))
