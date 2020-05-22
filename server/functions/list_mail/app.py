import json
import boto3

client = boto3.client('s3')


def lambda_handler(event, context):
    username = event['requestContext']['authorizer']['claims']['cognito:username']
    bucket = 'oscarhsu-nctu-bbs-{}'.format(username)
    result = []

    response = client.list_objects(
        Bucket=bucket,
        Prefix='mail'
    )

    for item in response['Contents']:
        tmp = item['Key'].replace("mail/", "").split("|")
        result.append(tmp)

    return {
        "statusCode": 200,
        "body": json.dumps(sorted(result, key=lambda k: k[2]))
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
        }
    }
    print(json.dumps(lambda_handler(event, {})))
