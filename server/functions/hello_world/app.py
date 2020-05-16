import json
import boto3

cloudformation = boto3.client('cloudformation')

def get_outputs():
    response = cloudformation.describe_stacks(
        StackName='NCTU-BBS'
    )
    outputs = {}
    for item in response['Stacks'][0]['Outputs']:
        outputs[item['OutputKey']] = item['OutputValue']
    return outputs

def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "********************************\n** Welcome to the BBS server. **\n********************************",
            "cognito_client_id": get_outputs()['UserPoolClientId']
        }),
    }
