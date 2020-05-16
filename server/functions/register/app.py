import json
import boto3

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
        ACL='public-read',
        Bucket='oscarhsu-nctu-bbs-' + username + '-post',
        CreateBucketConfiguration={
            'LocationConstraint': 'us-west-2'
        }
    )
    s3.create_bucket(
        ACL='private',
        Bucket='oscarhsu-nctu-bbs-' + username + '-mail',
        CreateBucketConfiguration={
            'LocationConstraint': 'us-west-2'
        }
    )
    return {
        "statusCode": 200
    }


if __name__ == "__main__":
    lambda_handler({'username': 'user0'}, {})
