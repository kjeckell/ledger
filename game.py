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
            - clubName (REQUIRED)
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
    if 'clubName' in payLoad:
        inClubName = payLoad['clubName']
        game['clubName'] = {'S': payLoad['clubName']}
    else:  # kill the whole thing if we don't get a club
        print('No Club Passed')
        print(payLoad)

    if 'playersList' in payLoad:
        game['playersList'] = {'S': payLoad['playersList']}
    else:  # kill the whole thing if we don't get a set of players
        print('No Players List Passed')
        print(payLoad)

    if 'dateStart' in payLoad:
        inStartDate = payLoad['dateStart']
        game['dateStart'] = {'S': payLoad['dateStart']}
    else:  # kill the whole thing if we don't get a start date
        print('No Start Date Passed')
        print(payLoad)
    
    # TODO: Test if this club already has a game on this date

    # Attempt to add the game to dynamodb
    gameUniqueKey = inClubName + '~' + inStartDate
    game['gameUniqueKey'] = {'S': gameUniqueKey}
    try:
        print('Trying to add: ' + gameUniqueKey)
        dynamodb.put_item(
            TableName=table,
            Item=game,
            ConditionExpression="attribute_not_exists(gameUniqueKey)"
        )
    except Exception as e:
        if e == 'ConditionalCheckFailedException':
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

def end_game(event, context):
    '''end_game is a Lambda Function used to close an active game (or reactivate)

        Inputs: 
            JSON formated Response Header (from API Gateway)
            - clubName (REQUIRED)
            - dateStart (REQUIRED)
            - reActivate
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
    if 'clubName' in payLoad:
        inClubName = payLoad['clubName']
        game['clubName'] = {'S': payLoad['clubName']}
    else:  # kill the whole thing if we don't get a club
        print('No Club Passed')
        print(payLoad)

    if 'dateStart' in payLoad:
        inStartDate = payLoad['dateStart']
        game['dateStart'] = {'S': payLoad['dateStart']}
    else:  # kill the whole thing if we don't get a start date
        print('No Start Date Passed')
        print(payLoad)

    gameUniqueKey = inClubName + '~' + inStartDate
    game['gameUniqueKey'] = {'S': gameUniqueKey}
    
    # If we pass the right thing, it will drop the attribute
    if 'reActivate' in payLoad:
        if (payLoad['reActivate'] != 1):
            game['deactivateGame'] = {'BOOL': True}
    else:
        game['deactivateGame'] = {'BOOL': True}
    
    try:
        print('Looking for ' + gameUniqueKey)
        response = dynamodb.get_item(
            TableName=table,
            Key={
                'gameUniqueKey': {'S': gameUniqueKey }
            }
        )
    except Exception as e:
        print(inClubName + ' game on ' + inStartDate + ' not found')
        print(e)
        retVal['statusCode'] = 500
        retVal['body'] = json.dumps(
            {'message': 'Game Not Found', 'success': False, 'game': {}})
        return retVal
    else:
        # Since we are just trying to deactivate, no need for more data validation
        try:
            print('Trying to update ' + gameUniqueKey)
            
            # Handle when a record has lost its playersList
            try:
                curPlayersList = response['Item']['playersList']['S']
            except KeyError:
                print('current game has not players list')
            else:
                game['playersList'] = { 'S': curPlayersList }

            dynamodb.put_item(TableName=table, Item=game)
        except Exception as e:
            print(gameUniqueKey + ' failed to update')
            print(e)
            retVal['statusCode'] = 500
            retVal['body'] = json.dumps(
                {'message': 'Game failed to update', 'success': False, 'game': {}})
            return retVal
        else:
            print(gameUniqueKey + " Updated")
            retVal['body'] = json.dumps(
                {'message': 'Game Ended', 'success': True, 'game': game})
            return retVal