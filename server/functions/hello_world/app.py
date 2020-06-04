import json
import boto3
import os

def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "********************************\n** Welcome to the BBS server. **\n********************************",
            "cognito_client_id": os.environ['USER_POOL_CLIENT_ID'],
            "websocket_url": os.environ['WEBSOCKET_URL']
        }),
    }
