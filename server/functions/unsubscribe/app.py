import json
import boto3
import os

client = boto3.client('dynamodb')


def lambda_handler(event, context):
    username = event['requestContext']['authorizer']['claims']['cognito:username']
    body = json.loads(event['body'])
    if "board" in body:
        unsub = body['board']
        table = os.environ['BOARD_SUB_TABLE']
    elif "author" in body:
        unsub = body['author']
        table = os.environ['AUTHOR_SUB_TABLE']

    item = client.scan(
        TableName=table,
        FilterExpression="contains(#user, :username) and begins_with(#sub, :unsub)",
        ExpressionAttributeNames={
            "#user": "user",
            "#sub": "subscribe"
        },
        ExpressionAttributeValues={
            ":username": {"S": username},
            ":unsub": {"S": unsub + ":"}
        }
    )

    if item['Count'] == 0:
        return {
            "statusCode": 404,
            "body": json.dumps("You haven't subscribed " + unsub)
        }

    for i in item['Items']:
        client.update_item(
            TableName=table,
            Key={
                'subscribe': i['subscribe']
            },
            UpdateExpression="DELETE #u :l",
            ExpressionAttributeNames={
                '#u': 'user'
            },
            ExpressionAttributeValues={
                ':l': {'SS':[username]},
            }
        )


    return {
        "statusCode": 200,
        "body": json.dumps("Unsubscribe successfully.")
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
        },
        "body": '{"board": "b1"}'
    }
    os.environ['BOARD_SUB_TABLE'] = 'nctu-bbs-board-sub'
    os.environ['AUTHOR_SUB_TABLE'] = 'nctu-bbs-author-sub'
    print(lambda_handler(event, {}))
