import json
import boto3
import time
import os

s3 = boto3.client('s3')


def lambda_handler(event, context):
    key = json.loads(event['body'])['key']
    username = event['requestContext']['authorizer']['claims']['cognito:username']

    bucket = '{}-{}'.format(os.environ['BUCKET_PREFIX'], username)
    key = 'mail/{}'.format(key)

    s3.delete_object(
        Bucket=bucket,
        Key=key
    )

    return {
        "statusCode": 200
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
        "body": '{"key": "subject1|user0|"}'
    }
    print(lambda_handler(event, {}))
