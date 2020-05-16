import json

def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "********************************\n** Welcome to the BBS server. **\n********************************",
            "cognito_client_id": "79hl4aakiqf13mo05celgerq9f"
        }),
    }
