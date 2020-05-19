import json
import boto3

client = boto3.client('dynamodb')
s3 = boto3.client('s3')


def lambda_handler(event, context):
    post_id = json.loads(event['body'])['post_id']
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
        if owner != username:
            return {
                "statusCode": 401,
                "body": json.dumps("Not the post owner.")
            }
        s3.delete_object(
            Bucket='oscarhsu-nctu-bbs-' + username,
            Key='post/{}-{}'.format(item['Item']['title']['S'], item['Item']['date']['S']))

        client.delete_item(
            TableName='nctu-bbs-posts',
            Key={
                'id': {
                    'N': post_id,
                }
            })
        return {
            "statusCode": 200,
            "body": json.dumps("Delete successfully.")
        }
    except KeyError:
        return {
            "statusCode": 404,
            "body": json.dumps("Post does not exist.")
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
        "body": '{"post_id": "3"}'
    }
    print(json.dumps(lambda_handler(event, {})))
