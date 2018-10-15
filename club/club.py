from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal
import os

# Default container for returns to API Gateway
# you will need to add a 'body' key with a JSON
# string containing the intended response
retVal = {"isBase64Encoded": False, "statusCode": 200,"headers": {"Access-Control-Allow-Origin": '*', "Access-Control-Allow-Credentials": True}}
table = os.environ['ClubTableName']

def add_club(event, context):
    '''add_club is a Lambda Function used to insert a club record

        Inputs: 
            JSON formated Response Header (from API Gateway)
            - email: string (REQUIRED)
            - clubName: string
            - nickName: string
        Outputs:
            JSON formated string containing
            - message: function outcome
            - success: True/False if the insert succeeded
            - club: submitted club object
    '''
    dynamodb = boto3.client('dynamodb')
    club = {} # will be used to track what we put in DynamoDB

    # Pull the passed data into python objects
    payLoad = event['body'] # API Gateway passes unencoded json (read: string) in body
    payLoad = json.loads(payLoad) # Encode string into json (read: dict)

    # Data validation and testing if data exists
    if 'email' in payLoad:
        inEmail = payLoad['email']
        club['email'] = {'S': payLoad['email']}
    else: # kill the whole thing if we don't get a club email
        print('No Email Passed')
        print(payLoad)

    if 'clubName' in payLoad:
        club['clubName'] = {'S': payLoad['clubName']}

    if 'nickName' in payLoad:
        club['nickName'] = {'S': payLoad['nickName']}

    # Attempt to add the club to dynamodb
    try:
        print('Trying to add: ' + inEmail)
        response = dynamodb.put_item(
            TableName=table, 
            Item=club,
            ConditionExpression="attribute_not_exists(email)"
        )
    except Exception as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print(inEmail + ' already exists in table ' + table)
            # Adding the 'body' key and contents for delivery back to requestor
            retVal['body'] = json.dumps({'message': 'Email already exists', 'success': False, 'club': {}})
            return retVal
        else:
            print("Unhandled Error")
            print(e)
    else:
        print(inEmail + " Created")
        # Adding the 'body' key and contents for delivery back to requestor
        retVal['body'] = json.dumps({'message': 'Club Added', 'success': True, 'club': club})
        return retVal
        
def get_club(event, context):
    '''get_club is a Lambda Function used to return a single club record

        Inputs: 
            Query String (from API Gateway)
            - email: string (REQUIRED)
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
        if 'email' in qsParams:
            inEmail = qsParams['email']

            # Attempt to get a response from dynamodb
            try:
                print('Trying to find ' + inEmail)
                response = dynamodb.get_item(
                    TableName = table,
                    Key = {
                        'email' : {'S' : str(qsParams['email'])}
                    }
                )
            except Exception as e:
                print(e)

                retVal['body'] = json.dumps({'message': 'No Club Found', 'success': False, 'player': {}})
                return retVal
            else:
                print(inEmail + " Returned")
                club = response['Item']

                retVal['body'] = json.dumps({'message': 'Club Returned', 'success': True, 'club': club})
                return retVal
    
def update_club(event, context):
    '''update_club is a Lambda Function used to update any value for a single club record

        Inputs: 
            JSON formated Response Header (from API Gateway)
            - email: string (REQUIRED)
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
    payLoad = event['body'] # API Gateway passes unencoded json (read: string) in body
    payLoad = json.loads(payLoad) # Encode string into json (read: dict)

    # Need to valdiate that we got an email in the payload
    if 'email' in payLoad:
        # We first want to verify that the club exists in our table
        try:
            print('Looking for ' + payLoad['email'])
            response = dynamodb.get_item(
                TableName = table,
                Key = {
                    'email' : {'S' : str(payLoad['email'])}
                }
            )
        except Exception as e:
            # TODO: Build specific handling for club not found vs generic something went wrong
            print(payLoad['email'] + ' not found')
            print(e)
            retVal['body'] = json.dumps({'message': 'Club Not Found', 'success': False, 'club': {}})
            return retVal
        else:
            print(payLoad['email'] + ' was found')
            club = response['Item'] # taking the existing club object in from the initial search

            # Validate what data we got in the payload to do updates with
            if 'clubName' in payLoad:
                club['clubName'] = {'S': payLoad['clubName'] }

            if 'nickName' in payLoad:
                club['nickName'] = {'S': payLoad['nickName'] }
                
            # Need to try updating the club record we found
            try:
                print('Trying to update ' + payLoad['email'])
                dynamodb.put_item(TableName=table, Item=club)
            except Exception as e:
                print(payLoad['email'] + ' failed to update')
                print(e)
                retVal['body'] = json.dumps({'message': 'Club Not Found', 'success': False, 'club': {}})
                return retVal
            else:
                print(payLoad['email'] + " Updated")
                retVal['body'] = json.dumps({'message': 'Club Updated', 'success': True, 'club': club})
                return retVal
    # We never got an email in the payload so we cant update anything
    else:
        retVal['body'] = json.dumps({'message': 'No Email Recieved', 'success': False, 'club': {}})
        return retVal