import json
import boto3
from datetime import datetime

client = boto3.client('dynamodb')
s3 = boto3.client('s3')


def lambda_handler(event, context):
    body = json.loads(event['body'])
    username = json.dumps(event['requestContext']['authorizer']['claims']['cognito:username'])
    board = body['board']
    title = body['title']
    content = body['content']

    item = client.get_item(
        TableName='nctu-bbs-boards',
        Key={'name': {'S': board}})

    if not "Item" in item:
        return {
            "statusCode": 400,
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
    date = datetime.now().strftime("%Y-%m-%d")
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
            }
        })

    body['date'] = date
    body['comment'] = {}
    response = s3.put_object(
        ACL='public-read',
        Body=json.dumps(body).encode(),
        Bucket=bucket,
        Key=key)

    return {
        "statusCode": 200,
        "body": json.dumps("Create post successfully.")
    }


if __name__ == "__main__":
    event = {
        "body": '{"username": "user0", "board": "board0", "title":"title", "content":"content"}'
    }
    print(json.dumps(lambda_handler(event, {})))
