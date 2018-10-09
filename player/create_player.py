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

    if (event["queryStringParameters"] is not None): # verify we got query strings
        qsParams = event["queryStringParameters"]

        if 'email' in qsParams:
            inEmail =  qsParams['email']
            item['email'] = {'S': qsParams['email']}
        else: # kill the whole thing if we don't get a club name
            print('No Email Passed')
            print(qsParams)
    
        if 'fullName' in qsParams:
            item['fullName'] = {'S': qsParams['fullName']}

        if 'nickName' in qsParams:
            item['nickName'] = {'S': qsParams['nickName']}

        print('Adding: ' + inEmail)

        try:
            response = dynamodb.put_item(
                TableName=table, 
                Item=item,
                ConditionExpression="attribute_not_exists(email)"
            )
        except Exception as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                print('Email Already Exists')

                return {
                    "statusCode": 417
                }
        else:
            print("Player Created")
        
            # This allows the API to not return 502 Bad Gateway
            return {
                "statusCode": 200
            }