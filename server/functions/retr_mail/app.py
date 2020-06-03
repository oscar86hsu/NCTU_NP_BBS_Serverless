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

    response = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': bucket,
            'Key': key
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
        "body": '{"key": "subject1|user1|1590162959"}'
    }
    print(lambda_handler(event, {}))
