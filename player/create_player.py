from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    dynamodb = boto3.client('dynamodb')
    table = 'player'
    item = {} # will be used to track what we put in DynamoDB
    payLoad = event['body'] # API Gateway passes unencoded json (read: string) in body
    payLoad = json.loads(payLoad) # Encode string into json (read: dict)

    if 'email' in payLoad:
        inEmail = payLoad['email']
        item['email'] = {'S': payLoad['email']}
    else: # kill the whole thing if we don't get a club name
        print('No Email Passed')
        print(payLoad)

    if 'fullName' in payLoad:
        item['fullName'] = {'S': payLoad['fullName']}

    if 'nickName' in payLoad:
        item['nickName'] = {'S': payLoad['nickName']}

    print('Trying to add: ' + inEmail)

    try:
        response = dynamodb.put_item(
            TableName=table, 
            Item=item,
            ConditionExpression="attribute_not_exists(email)"
        )
    except Exception as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print(inEmail + ' already exists in table ' + table)

            return {
                "isBase64Encoded": False,
                "statusCode": 200,
                "headers": {},
                'body': json.dumps({
                    'resultText': 'Email already exists',
                    'result': False
                })
            }
    else:
        print("Player Created")
    
        # This allows the API to not return 502 Bad Gateway
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {},
            'body': json.dumps({
                'resultText': 'Player Added!',
                'result': True
            })
        }