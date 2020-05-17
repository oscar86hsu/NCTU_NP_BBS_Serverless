import json
import boto3

client = boto3.client('dynamodb')


def lambda_handler(event, context):
    username = json.loads(event['body'])['username']
    boardname = json.loads(event['body'])['boardname']

    try:
        client.put_item(
            TableName='nctu-bbs-boards',
            Item={
                'name': {
                    'S': boardname
                },
                'moderator': {
                    'S': username
                }
            },
            ConditionExpression= "#bname <> :boardname",
            ExpressionAttributeNames= {
                "#bname": "name"
            },
            ExpressionAttributeValues= {
                ":boardname" : {"S": boardname}
            })
    except client.exceptions.ConditionalCheckFailedException:
        return {
            "statusCode": 200,
            "body": json.dumps("Board already exist.")
        }

    return {
        "statusCode": 200,
        "body": json.dumps("Create board successfully.")
    }


if __name__ == "__main__":
    event = {
        "body": '{"username": "user0", "boardname": "board0"}'
    }
    lambda_handler(event, {})
