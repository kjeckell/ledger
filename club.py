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


def add_club(event, context):
    '''add_club is a Lambda Function used to insert a club record

        Inputs: 
            JSON formated Response Header (from API Gateway)
            - clubName: string (REQUIRED)
            - nickName: string
        Outputs:
            JSON formated string containing
            - message: function outcome
            - success: True/False if the insert succeeded
            - club: submitted club object
    '''
    dynamodb = boto3.client('dynamodb')
    club = {}  # will be used to track what we put in DynamoDB

    # Pull the passed data into python objects
    # API Gateway passes unencoded json (read: string) in body
    payLoad = event['body']
    payLoad = json.loads(payLoad)  # Encode string into json (read: dict)

    # Data validation and testing if data exists
    if 'clubName' in payLoad:
        inClubName = payLoad['clubName']
        club['clubName'] = {'S': payLoad['clubName']}

    if 'nickName' in payLoad:
        club['nickName'] = {'S': payLoad['nickName']}

    # Attempt to add the club to dynamodb
    try:
        print('Trying to add: ' + inClubName)
        response = dynamodb.put_item(
            TableName=table,
            Item=club,
            ConditionExpression="attribute_not_exists(clubName)"
        )
    except Exception as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print(inClubName + ' already exists in table ' + table)
            # Adding the 'body' key and contents for delivery back to requestor
            retVal['body'] = json.dumps(
                {'message': 'Club already exists', 'success': False, 'club': {}})
            return retVal
        else:
            print("Unhandled Error")
            print(e)
    else:
        print(inClubName + " Created")
        # Adding the 'body' key and contents for delivery back to requestor
        retVal['body'] = json.dumps(
            {'message': 'Club Added', 'success': True, 'club': club})
        return retVal


def get_club(event, context):
    '''get_club is a Lambda Function used to return a single club record

        Inputs: 
            Query String (from API Gateway)
            - clubName: string (REQUIRED)
        Outputs:
            JSON formated string containing
            - message: function outcome
            - success: True/False if the insert succeeded
            - club: club object
    '''
    dynamodb = boto3.client('dynamodb')

    # Need to validate that we actually recieved query string parameters
    if (event["queryStringParameters"] is not None):
        qsParams = event["queryStringParameters"]

        # Validate that we recieved a key 'email' in the query string
        if 'clubName' in qsParams:
            inClubName = qsParams['clubName']

            # Attempt to get a response from dynamodb
            try:
                print('Trying to find ' + inClubName)
                response = dynamodb.get_item(
                    TableName=table,
                    Key={
                        'clubName': {'S': str(qsParams['clubName'])}
                    }
                )
            except Exception as e:
                print(e)

                retVal['body'] = json.dumps(
                    {'message': 'No Club Found', 'success': False, 'club': {}})
                return retVal
            else:
                print(inClubName + " Returned")
                club = response['Item']

                retVal['body'] = json.dumps(
                    {'message': 'Club Returned', 'success': True, 'club': club})
                return retVal


def update_club(event, context):
    '''update_club is a Lambda Function used to update any value for a single club record

        Inputs: 
            JSON formated Response Header (from API Gateway)
            - clubName: string
            - nickName: string
        Outputs:
            JSON formated string containing
            - message: function outcome
            - success: True/False if the update succeeded
            - club: club object
    '''
    dynamodb = boto3.client('dynamodb')

    # Pull the passed data into python objects
    # API Gateway passes unencoded json (read: string) in body
    payLoad = event['body']
    payLoad = json.loads(payLoad)  # Encode string into json (read: dict)

    # Need to valdiate that we got an email in the payload
    if 'clubName' in payLoad:
        # We first want to verify that the club exists in our table
        try:
            print('Looking for ' + payLoad['clubName'])
            response = dynamodb.get_item(
                TableName=table,
                Key={
                    'clubName': {'S': str(payLoad['clubName'])}
                }
            )
        except Exception as e:
            # TODO: Build specific handling for club not found vs generic something went wrong
            print(payLoad['clubName'] + ' not found')
            print(e)
            retVal['statusCode'] = 500
            retVal['body'] = json.dumps(
                {'message': str(e), 'success': False, 'club': {}})
            return retVal
        else:
            print(payLoad['clubName'] + ' was found')
            # taking the existing club object in from the initial search
            club = response['Item']

            # Validate what data we got in the payload to do updates with
            if 'clubName' in payLoad:
                club['clubName'] = {'S': payLoad['clubName']}

            if 'nickName' in payLoad:
                club['nickName'] = {'S': payLoad['nickName']}

            # Need to try updating the club record we found
            try:
                print('Trying to update ' + payLoad['clubName'])
                dynamodb.put_item(TableName=table, Item=club)
            except Exception as e:
                print(payLoad['clubName'] + ' failed to update')
                print(e)
                retVal['statusCode'] = 500
                retVal['body'] = json.dumps(
                    {'message': str(e), 'success': False, 'club': {}})
                return retVal
            else:
                print(payLoad['clubName'] + " Updated")
                retVal['body'] = json.dumps(
                    {'message': 'Club Updated', 'success': True, 'club': club})
                return retVal
    # We never got an email in the payload so we cant update anything
    else:
        retVal['body'] = json.dumps(
            {'message': 'No Club Name Recieved', 'success': False, 'club': {}})
        return retVal
