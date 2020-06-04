import json
import boto3
import os

dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    connection_id = event["requestContext"].get("connectionId")
    username = event['headers']['username']

    if event["requestContext"]["eventType"] == "CONNECT":

        if not connection_id:
            return {"statusCode": 500, "body": json.dumps("Connection ID value not set.")}

        table = dynamodb.Table(os.environ['CONNECTION_TABLE'])
        table.put_item(Item={"connection_id": connection_id, "username": username})
        return {"statusCode": 200, "body": json.dumps("Connect successful.")}

    elif event["requestContext"]["eventType"] == "DISCONNECT":

        if not connection_id:
            return {"statusCode": 500, "body": json.dumps("Connection ID value not set.")}

        table = dynamodb.Table(os.environ['CONNECTION_TABLE'])
        table.delete_item(Key={"username": username})
        return {"statusCode": 200, "body": json.dumps("Disconnect successful.")}

    else:
        return {"statusCode": 500, "body": json.dumps("Unrecognized eventType.")}


def default_message(event, context):
    return {"statusCode": 400, "body": json.dumps("Unrecognized WebSocket action.")}