import json
import boto3
import os

client = boto3.client('dynamodb')


def lambda_handler(event, context):
    username = event['requestContext']['authorizer']['claims']['cognito:username']
    body = json.loads(event['body'])
    if "board" in body:
        subs = body['board']
        table = os.environ['BOARD_SUB_TABLE']
    elif "author" in body:
        subs = body['author']
        table = os.environ['AUTHOR_SUB_TABLE']
    keyword = json.loads(event['body'])['keyword']


    item = client.get_item(
        TableName=table,
        Key={'subscribe': {'S': '{}:{}'.format(subs, keyword)}})

    if "Item" in item:
        try:
            for user in item['Item']['user']['SS']:
                if user == username:
                    return {
                        "statusCode": 406,
                        "body": json.dumps("Already subscribed.")
                    }
        except KeyError:
            pass

    client.update_item(
        TableName=table,
        Key={
            'subscribe': {'S':'{}:{}'.format(subs, keyword)}
        },
        UpdateExpression="ADD #u :l",
        ExpressionAttributeNames={
            '#u': 'user'
        },
        ExpressionAttributeValues={
            ':l': {'SS':[username]},
        }
    )

    return {
        "statusCode": 200,
        "body": json.dumps("Subscribe successfully.")
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
        "body": '{"keyword": "aws", "board": "b1"}'
    }
    os.environ['BOARD_SUB_TABLE'] = 'nctu-bbs-board-sub'
    os.environ['AUTHOR_SUB_TABLE'] = 'nctu-bbs-author-sub'
    print(lambda_handler(event, {}))
