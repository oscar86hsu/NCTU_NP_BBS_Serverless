import json
import boto3
import os

dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    print(event)
    connection_id = event["requestContext"].get("connectionId")
    # username = event['requestContext']['authorizer']['claims']['cognito:username']
    username = "aaa"

    if event["requestContext"]["eventType"] == "CONNECT":

        # Ensure connection_id and token are set
        if not connection_id:
            return {"statusCode": 500, "body": json.dumps("Connection ID value not set.")}
        # if not token:
        #     logger.debug("Failed: token query parameter not provided.")
        #     return _get_response(400, "token query parameter not provided.")

        # Verify the token
        # try:
        #     payload = jwt.decode(token, "FAKE_SECRET", algorithms="HS256")
        #     logger.info("Verified JWT for '{}'".format(payload.get("username")))
        # except:
        #     logger.debug("Failed: Token verification failed.")
        #     return _get_response(400, "Token verification failed.")

        # Add connection_id to the database
        table = dynamodb.Table(os.environ['CONNECTION_TABLE'])
        table.put_item(Item={"connection_id": connection_id, "username": username})
        return {"statusCode": 200, "body": json.dumps("Connect successful.")}

    elif event["requestContext"]["eventType"] == "DISCONNECT":

        # Ensure connection_id is set
        if not connection_id:
            return {"statusCode": 500, "body": json.dumps("Connection ID value not set.")}

        # Remove the connection_id from the database
        table = dynamodb.Table(os.environ['CONNECTION_TABLE'])
        table.delete_item(Key={"username": username})
        return {"statusCode": 200, "body": json.dumps("Disconnect successful.")}

    else:
        return {"statusCode": 500, "body": json.dumps("Unrecognized eventType.")}


def default_message(event, context):
    """
    Send back error when unrecognized WebSocket action is received.
    """
    return {"statusCode": 400, "body": json.dumps("Unrecognized WebSocket action.")}