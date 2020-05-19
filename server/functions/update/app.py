import json
import boto3

client = boto3.client('dynamodb')
s3 = boto3.client('s3')


def lambda_handler(event, context):
    body = json.loads(event['body'])
    post_id = body['post_id']
    update = body['update']
    content = body['content']
    username = event['requestContext']['authorizer']['claims']['cognito:username']

    item = client.get_item(
        TableName='nctu-bbs-posts',
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

    if update == 'comment':
        pass
    else:
        if owner != username:
            return {
                "statusCode": 401,
                "body": json.dumps("Not the post owner.")
            }
        response = s3.get_object(Bucket='oscarhsu-nctu-bbs-' + owner,
                                 Key='post/{}-{}'.format(title, date))

        post = json.loads(response['Body'].read())
        post[update[2:]] = content
        if update == '--title':
            bucket = 'oscarhsu-nctu-bbs-{}'.format(username)
            title = content
            key = 'post/{}-{}'.format(title, date)
            path = 'https://{}.s3.ap-northeast-1.amazonaws.com/{}'.format(
                bucket, key)
            s3.delete_object(
                Bucket='oscarhsu-nctu-bbs-' + username,
                Key='post/{}-{}'.format(title, date))

            client.update_item(
                TableName='nctu-bbs-posts',
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
            Bucket='oscarhsu-nctu-bbs-' + owner,
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
                    'cognito:username': 'user0'
                }
            }
        },
        "body": '{"post_id": "6", "update":"--title", "content":"new title 123"}'
    }
    print(json.dumps(lambda_handler(event, {})))
