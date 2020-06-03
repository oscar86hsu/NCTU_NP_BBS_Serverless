import json
import boto3
import time
import os

s3 = boto3.client('s3')


def lambda_handler(event, context):
    body = json.loads(event['body'])
    username = event['requestContext']['authorizer']['claims']['cognito:username']
    receiver = body['to']
    subject = body['subject']

    bucket = '{}-{}'.format(os.environ['BUCKET_PREFIX'], receiver)
    key = 'mail/{}|{}|{}'.format(subject, username, int(time.time()))

    response = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': bucket,
            'Key': key,
            'ACL': 'private'
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
                    'cognito:username': 'user1'
                }
            }
        },
        "body": '{"to": "user0", "subject":"subject2"}'
    }
    print(json.loads(lambda_handler(event, {})['body']))
