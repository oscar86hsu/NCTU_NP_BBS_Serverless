import json
import boto3
import os

client = boto3.client('dynamodb')


def lambda_handler(event, context):
    username = event['requestContext']['authorizer']['claims']['cognito:username']
    boardname = json.loads(event['body'])['boardname']

    try:
        client.put_item(
            TableName=os.environ['BOARDS_TABLE'],
            Item={
                'name': {
                    'S': boardname
                },
                'moderator': {
                    'S': username
                }
            },
            ConditionExpression= "#bname <> :boardname",
            ExpressionAttributeNames= {
                "#bname": "name"
            },
            ExpressionAttributeValues= {
                ":boardname" : {"S": boardname}
            })
    except client.exceptions.ConditionalCheckFailedException:
        return {
            "statusCode": 200,
            "body": json.dumps("Board already exist.")
        }

    return {
        "statusCode": 200,
        "body": json.dumps("Create board successfully.")
    }


if __name__ == "__main__":
    event = {
        'requestContext':
        {
            'authorizer':
            {
                'claims':
                {
                    'cognito:username': 'user0'
                }
            }
        },
        "body": '{"username": "user0", "boardname": "board0"}'
    }
    print(lambda_handler(event, {}))
