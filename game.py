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


def start_game(event, context):
    '''start_game is a Lambda Function used to initiate a new game

        Inputs: 
            JSON formated Response Header (from API Gateway)
            - clubId (REQUIRED)
            - playersList (REQUIRED)
            - dateStart (REQUIRED)
        Outputs:
            JSON formated string containing
            - message: function outcome
            - success: True/False if the insert succeeded
            - game: submitted game object
    '''
    dynamodb = boto3.client('dynamodb')
    game = {}  # will be used to track what we put in DynamoDB

    # Pull the passed data into python objects
    # API Gateway passes unencoded json (read: string) in body
    payLoad = event['body']
    payLoad = json.loads(payLoad)  # Encode string into json (read: dict)

    # Data validation and testing if data exists
    if 'clubId' in payLoad:
        inClubId = payLoad['clubId']
        game['clubId'] = {'S': payLoad['clubId']}
    else:  # kill the whole thing if we don't get a club
        print('No Club Passed')
        print(payLoad)

    if 'playersList' in payLoad:
        inPlayersList = payLoad['playersList']
        game['playersList'] = {'S': payLoad['playersList']}
    else:  # kill the whole thing if we don't get a set of players
        print('No Players List Passed')
        print(payLoad)

    if 'dateStart' in payLoad:
        inDateStart = payLoad['dateStart']
        game['dateStart'] = {'S': payLoad['dateStart']}
    else:  # kill the whole thing if we don't get a start date
        print('No Start Date Passed')
        print(payLoad)
    
    # TODO: Test if this club already has a game on this date

    # Attempt to add the game to dynamodb
    gameUniqueKey = inClubId + '~' + inDateStart
    game['gameUniqueKey'] = {'S': gameUniqueKey}
    try:
        print('Trying to add: ' + gameUniqueKey)
        response = dynamodb.put_item(
            TableName=table,
            Item=game,
            ConditionExpression="attribute_not_exists(gameUniqueKey)"
        )
    except Exception as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print('This club already has a game on that day in ' + table)
            # Adding the 'body' key and contents for delivery back to requestor
            retVal['body'] = json.dumps(
                {'message': 'Game already exists', 'success': False, 'game': {}})
            return retVal
        else:
            print('Unhandled Error')
            print(e)
    else:
        print('Game Created')
        # Adding the 'body' key and contents for delivery back to requestor
        retVal['body'] = json.dumps(
            {'message': 'Game Added', 'success': True, 'game': game})
        return retVal