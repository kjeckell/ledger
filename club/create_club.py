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
    table = 'club'
    item = {} # will be used to track what we put in DynamoDB
    
    if (event["queryStringParameters"] is not None): # verify we got query strings
        qsParams = event["queryStringParameters"]
        
        if 'club' in qsParams:
            inClubName =  qsParams['club']
            item['clubName'] = {'S': qsParams['club']}
        else: # kill the whole thing if we don't get a club name
            print('No Club Passed')
            print(qsParams)
    
        if 'owner' in qsParams:
            item['owner'] = {'S': qsParams['owner']}
        else: # kill the whole thing if we don't get a club name
            print('No Owner Passed')
            print(qsParams)

        if 'since' in qsParams:
            item['sinceDate'] = {'S': qsParams['since']}

        if 'logoPath' in qsParams:
            item['logo'] = {'S': qsParams['logoPath']}

        print('Adding: ' + inClubName)

        try:
            response = dynamodb.put_item(
                TableName=table, 
                Item=item,
                ConditionExpression="attribute_not_exists(clubName)"
            )
        except Exception as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                print('Club Already Exists')

                return {
                    "statusCode": 417
                }
        else:
            print("Ledger Created")
        
            # This allows the API to not return 502 Bad Gateway
            return {
                "statusCode": 200
            }