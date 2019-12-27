from __future__ import print_function  # Python 2/3 compatibility
import boto3
import json
import decimal
import os

# Default container for returns to API Gateway
# you will need to add a 'body' key with a JSON
# string containing the intended response
retVal = {"isBase64Encoded": False, "statusCode": 200, "headers": {
    "Access-Control-Allow-Origin": '*', "Access-Control-Allow-Credentials": True}}
table = os.environ['ClubTableName']


def get_clubs(event, context):
    '''get_clubs is a Lambda Function used to return all players

        Inputs: 
        Outputs:
            JSON formated string containing
            - message: function outcome
            - success: True/False if the insert succeeded
            - clubs: all clubs in a single dict
    '''
    dynamodb = boto3.client('dynamodb')

    try:
        print('Attempting to scan ' + table)
        response = dynamodb.scan(
            TableName=table
        )
    except Exception as e:
        print('Scan failed')
        print(e)

        retVal['body'] = json.dumps(
            {'message': 'Unable to search table', 'success': False, 'clubs': {}})
        retVal['statusCode'] = 500
        return retVal
    else:
        print("Clubs Returned")
        clubs = response['Items']

        retVal['body'] = json.dumps(
            {'message': 'Clubs Returned', 'success': True, 'clubs': clubs})
        return retVal
