import json
import boto3
import os

client = boto3.client('dynamodb')
s3 = boto3.client('s3')


def lambda_handler(event, context):
    body = json.loads(event['body'])
    post_id = body['post_id']
    update = body['update']
    content = body['content']
    username = event['requestContext']['authorizer']['claims']['cognito:username']

    item = client.get_item(
        TableName=os.environ['POSTS_TABLE'],
        Key={
            'id': {
                'N': post_id,
            }
        })
    try:
        owner = item['Item']['author']['S']
        title = item['Item']['title']['S']
        date = item['Item']['date']['S']
        path = item['Item']['path']['S']
        index = item['Item']['id']['N']
    except KeyError:
        return {
            "statusCode": 404,
            "body": json.dumps("Post does not exist.")
        }

    response = s3.get_object(Bucket='{}-{}'.format(os.environ['BUCKET_PREFIX'], owner),
                                 Key='post/{}-{}'.format(title, date))
    post = json.loads(response['Body'].read())

    if update == 'comment':
        post['comment'].append({'username': username, 'comment':content})
        s3.put_object(
            ACL='public-read',
            Body=json.dumps(post).encode(),
            Bucket='{}-{}'.format(os.environ['BUCKET_PREFIX'], owner),
            Key='post/{}-{}'.format(title, date))
        return {
            "statusCode": 200,
            "body": json.dumps("Comment successfully.")
        }
    else:
        if owner != username:
            return {
                "statusCode": 401,
                "body": json.dumps("Not the post owner.")
            }
        
        post[update[2:]] = content
        if update == '--title':
            bucket = '{}-{}'.format(os.environ['BUCKET_PREFIX'], username)
            title = content
            key = 'post/{}-{}'.format(title, date)
            path = 'https://{}.s3.ap-northeast-1.amazonaws.com/{}'.format(
                bucket, key)
            s3.delete_object(
                Bucket='{}-{}'.format(os.environ['BUCKET_PREFIX'], username),
                Key='post/{}-{}'.format(title, date))

            client.update_item(
                TableName=os.environ['POSTS_TABLE'],
                Key={
                    'id':
                    {'N': index}
                },
                UpdateExpression="set #urlpath = :p, title=:t",
                ExpressionAttributeNames={
                    "#urlpath": "path"
                },
                ExpressionAttributeValues={
                    ':p': {'S': path},
                    ':t': {'S': title}
                })

        s3.put_object(
            ACL='public-read',
            Body=json.dumps(post).encode(),
            Bucket='{}-{}'.format(os.environ['BUCKET_PREFIX'], owner),
            Key='post/{}-{}'.format(title, date))

        return {
            "statusCode": 200,
            "body": json.dumps("Update successfully.")
        }


if __name__ == "__main__":
    event = {
        'requestContext':
        {
            'authorizer':
            {
                'claims':
                {
                    'cognito:username': 'user1'
                }
            }
        },
        "body": '{"post_id": "1", "update":"comment", "content":"comment"}'
    }
    print(json.dumps(lambda_handler(event, {})))
