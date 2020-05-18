import json
import boto3

client = boto3.client('dynamodb')


def lambda_handler(event, context):
    post_id = json.loads(event['body'])['post_id']

    item = client.get_item(
        TableName='nctu-bbs-posts',
        Key={
            'id': {
                'N': post_id,
            }
        })

    try:
        post_path = item['Item']['path']['S']
        return {
            "statusCode": 200,
            "body": json.dumps(post_path)
        }
    except KeyError:
        return {
            "statusCode": 404,
            "body": json.dumps("Post does not exist.")
        }

if __name__ == "__main__":
    event = {
        "body": '{"post_id": "1"}'
    }
    print(json.dumps(lambda_handler(event, {})))