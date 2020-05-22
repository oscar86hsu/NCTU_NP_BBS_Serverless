import json
import boto3
from datetime import datetime, timedelta

client = boto3.client('dynamodb')
s3 = boto3.client('s3')


def lambda_handler(event, context):
    body = json.loads(event['body'])
    username = event['requestContext']['authorizer']['claims']['cognito:username']
    board = body['board']
    title = body['title']

    item = client.get_item(
        TableName='nctu-bbs-boards',
        Key={'name': {'S': board}})

    if not "Item" in item:
        return {
            "statusCode": 404,
            "body": json.dumps("Board does not exist.")
        }

    item = client.get_item(
        TableName='nctu-bbs-next-id',
        Key={'name': {'S': 'post'}})

    try:
        index = int(item['Item']['id']['N']) + 1
    except KeyError:
        index = 1
    bucket = 'oscarhsu-nctu-bbs-{}'.format(username)
    now = datetime.utcnow() + timedelta(hours=8)
    date = now.strftime("%m/%d")
    key = 'post/{}-{}'.format(title, date)
    path = 'https://{}.s3.ap-northeast-1.amazonaws.com/{}'.format(bucket, key)

    client.put_item(
        TableName='nctu-bbs-next-id',
        Item={
            'name': {
                'S': "post"
            },
            'id': {
                'N': str(index)
            }
        })

    client.put_item(
        TableName='nctu-bbs-posts',
        Item={
            'path': {
                'S': path
            },
            'id': {
                'N': str(index)
            },
            'title': {
                'S': title
            },
            'author': {
                'S': username
            },
            'date': {
                'S': date
            },
            'board': {
                'S': board
            }
        })

    response = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': bucket,
            'Key': key,
            'ACL': 'public-read',
            'ContentType': 'application/json'
        },
        ExpiresIn=60
    )

    return {
        "statusCode": 200,
        "body": json.dumps(response)
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
        "body": '{"board": "board0", "title":"title", "content":"content"}'
    }
    print(json.loads(lambda_handler(event, {})['body']))
