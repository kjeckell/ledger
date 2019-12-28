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
table = os.environ['GamesTableName']


def get_games(event, context):
    '''get_games is a Lambda Function used to return all active games

        Inputs: 
        Outputs:
            JSON formated string containing
            - message: function outcome
            - success: True/False if the insert succeeded
            - games: all active games in a single dict
    '''
    dynamodb = boto3.client('dynamodb')

    try:
        print('Attempting to scan ' + table)
        response = dynamodb.scan(
            TableName=table,
            FilterExpression="attribute_not_exists(deactivateGame)"
        )
    except Exception as e:
        print('Scan failed')
        print(e)

        retVal['body'] = json.dumps(
            {'message': 'Unable to search table', 'success': False, 'games': {}})
        retVal['statusCode'] = 500
        return retVal
    else:
        print("Games Returned")
        games = response['Items']

        retVal['body'] = json.dumps(
            {'message': 'Games Returned', 'success': True, 'games': games})
        return retVal
