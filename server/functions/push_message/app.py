import json
import boto3
import os

client = boto3.client('dynamodb')
gatewayapi = boto3.client("apigatewaymanagementapi", endpoint_url = "https://" + os.environ['WEBSOCKET_URL'])


def generate_message(author, board, title):
    l = max(len(author)+7, len(board)+6, len(title)+6, 14) + 7
    message = "    "
    for i in range(int((l-10)/2)):
        message += "*"
    message += " New Post "
    for i in range(int(l/2)-5):
        message += "*"
    
    if l % 2:
        message += "*"
    message += "\n    "

    message += "*  Author: {}".format(author)
    for i in range(l - len(author) - 12):
        message += " "
    message += "*\n    "

    message += "*  Board: {}".format(board)
    for i in range(l - len(board) - 11):
        message += " "
    message += "*\n    "

    message += "*  Title: {}".format(title)
    for i in range(l - len(title) - 11):
        message += " "
    message += "*\n    "

    for i in range(l):
        message += "*"

    message += "\n% "
    return message

def lambda_handler(event, context):
    for record in event['Records']:
        notify = set()
        if record['eventName'] != 'INSERT':
            continue
        item = record['dynamodb']['NewImage']
        response = client.scan(
            TableName=os.environ['AUTHOR_SUB_TABLE'],
            FilterExpression="begins_with(#sub, :author)",
            ExpressionAttributeNames={
                "#sub": "subscribe"
            },
            ExpressionAttributeValues={
                ":author": {"S": item['author']['S'] + ":"}
            }
        )
        for i in response['Items']:
            keyword = i['subscribe']['S'].split(":")[1]
            if keyword in item['title']['S']:
                for user in i['user']['SS']:
                    notify.add(user)

        response = client.scan(
            TableName=os.environ['BOARD_SUB_TABLE'],
            FilterExpression="begins_with(#sub, :board)",
            ExpressionAttributeNames={
                "#sub": "subscribe"
            },
            ExpressionAttributeValues={
                ":board": {"S": item['board']['S'] + ":"}
            }
        )
        for i in response['Items']:
            keyword = i['subscribe']['S'].split(":")[1]
            if keyword in item['title']['S']:
                for user in i['user']['SS']:
                    notify.add(user)

        message = generate_message(item['author']['S'], item['board']['S'], item['title']['S'])
        for user in notify:
            response = client.scan(
                TableName=os.environ['CONNECTION_TABLE'],
                FilterExpression="#user = :username",
                ExpressionAttributeNames={
                    "#user": "username"
                },
                ExpressionAttributeValues={
                    ":username": {"S": user}
                }
            )
            for i in response['Items']:
                gatewayapi.post_to_connection(ConnectionId=i['connection_id']['S'], Data=json.dumps(message).encode('utf-8'))

if __name__ == "__main__":
    print(generate_message("aaa", "board", "This is another title"))