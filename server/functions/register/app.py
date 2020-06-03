import json
import boto3
import os

cognito = boto3.client('cognito-idp')
cloudformation = boto3.client('cloudformation')
s3 = boto3.client('s3')


def get_outputs():
    response = cloudformation.describe_stacks(
        StackName='NCTU-BBS'
    )
    outputs = {}
    for item in response['Stacks'][0]['Outputs']:
        outputs[item['OutputKey']] = item['OutputValue']
    return outputs


def lambda_handler(event, context):
    username = json.loads(event['body'])['username']
    outputs = get_outputs()

    cognito.admin_confirm_sign_up(
        UserPoolId=outputs['UserPoolId'],
        Username=username
    )

    s3.create_bucket(
        ACL='private',
        Bucket='{}-{}'.format(os.environ['BUCKET_PREFIX'], username),
        CreateBucketConfiguration={
            'LocationConstraint': 'ap-northeast-1'
        }
    )

    return {
        "statusCode": 200
    }

