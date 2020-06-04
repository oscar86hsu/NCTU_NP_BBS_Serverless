import json
import boto3
import os
import hashlib

client = boto3.client('cognito-idp')

def lambda_handler(event, context):
    username = event['headers']['username']
    password = event['headers']['password']
    tmp = event['methodArn'].split(':')
    apiGatewayArnTmp = tmp[5].split('/')

    client.initiate_auth(
        ClientId=os.environ['USER_POOL_CLIENT_ID'],
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': username,
            'PASSWORD': password
        }
    )

    authResponse = {
        "principalId": username,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": "arn:aws:execute-api:{}:{}:{}/*".format(tmp[3], tmp[4], apiGatewayArnTmp[0])
                }
            ]
        }
    }

    return authResponse

if __name__ == "__main__":
    event = {
        "headers":
        {
            "username": "aaa",
            "password": "ce6476478b73335a4f41e025e6d6afbd64bdbcff391ca626b5c8f964e959a6e1"
        }
    }
    os.environ['USER_POOL_CLIENT_ID'] = '2k12khg8cgtltsvg2835b135ul'
    lambda_handler(event, {})
