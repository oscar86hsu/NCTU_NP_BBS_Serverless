import json
import boto3

client = boto3.client('dynamodb')


def lambda_handler(event, context):
    key = json.loads(event['body'])['key']
    results = "    {:10}{:15}{:15}\n".format("Index", "Name", "Moderator")
    index = 0

    response = client.scan(TableName='nctu-bbs-boards')
    for item in response['Items']:
        if (len(key) > 0) and (key not in item['name']['S']):
            continue
        index += 1
        results += "    {:10}{:15}{:15}\n".format(
            str(index), item['name']['S'], item['moderator']['S'])

    return {
        "statusCode": 200,
        "body": json.dumps(results[:-1])
    }

