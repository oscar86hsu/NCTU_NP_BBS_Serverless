import json
import boto3

client = boto3.client('dynamodb')


def lambda_handler(event, context):
    key = json.loads(event['body'])['key']
    board = json.loads(event['body'])['board']

    item = client.get_item(
        TableName='nctu-bbs-boards',
        Key={'name': {'S': board}})

    if not "Item" in item:
        return {
            "statusCode": 404,
            "body": json.dumps("Board does not exist.")
        }
    
    results = "{:8}{:12}{:12}{:12}\n".format("ID", "Title", "Author", "Date")
    response = client.scan(TableName='nctu-bbs-posts')
    for item in response['Items']:
        if board != item['board']['S']:
            continue
        if (len(key) > 0) and (key not in item['title']['S']):
            continue
        results += "{:8}{:12}{:12}{:12}\n".format(item['id']['N'], item['title']['S'], item['author']['S'], item['date']['S'])

    return {
        "statusCode": 200,
        "body": json.dumps(results)
    }

if __name__ == "__main__":
    event = {
        "body": '{"board": "board0", "key":"new"}'
    }
    print(json.dumps(lambda_handler(event, {})))
