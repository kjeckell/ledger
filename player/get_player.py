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
    
    #fe = Key('col').between(val, val)
    #pe = "#projCol, Col, Col.Key"
    # Expression Attribute Names for Projection Expression only.
    #ean = { "#projCol": "Col", }
    
    try:
        response = dynamodb.scan(
            TableName = table
        )
    except Exception as e:
        print(e.response['Error']['Message'])

        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": '*'
            },
            'body': json.dumps({
                'players': ''players'',
                'success': False
            })
        }
    else:
        print("Players Returned")
        players = response['Items']

        # This allows the API to not return 502 Bad Gateway
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": '*'
            },
            'body': json.dumps({
                'players': players,
                'success': True
            })
        }