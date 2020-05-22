import json
import boto3
from datetime import datetime

s3 = boto3.client('s3')


def lambda_handler(event, context):
    body = json.loads(event['body'])
    username = event['requestContext']['authorizer']['claims']['cognito:username']
    receiver = body['to']
    subject = body['subject']

    bucket = 'oscarhsu-nctu-bbs-{}'.format(receiver)
    date = datetime.now().strftime("%Y-%m-%d")
    key = 'mail/{}-{}'.format(subject, date)

    response = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': bucket,
            'Key': key,
            'ACL': 'private',
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
        "body": '{"to": "user0", "subject":"subject"}'
    }
    print(json.loads(lambda_handler(event, {})['body']))
