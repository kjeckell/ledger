from __future__ import print_function  # Python 2/3 compatibility
import boto3
import json
import os
import uuid
from datetime import datetime

# Default container for returns to API Gateway
# you will need to add a 'body' key with a JSON
# string containing the intended response
retVal = {"isBase64Encoded": False, "statusCode": 200, "headers": {
    "Access-Control-Allow-Origin": '*', "Access-Control-Allow-Credentials": True}}
table = os.environ['GameLedgerTableName']

def add_ledger_entry(event, context):
    '''add_ledger_entry is a Lambda Function used to add records to gameLedger

        Inputs: 
            - gameUniqueID
            - fromPlayerEmail
            - toPlayerEmail
            - dollarAmt
        Outputs:
            JSON formated string containing
            - message: function outcome
            - success: True/False if the insert succeeded
    '''
    dynamodb = boto3.client('dynamodb')
    ledgerEntry = {}

    # Pull the passed data into python objects
    # API Gateway passes unencoded json (read: string) in body
    payLoad = event['body']
    payLoad = json.loads(payLoad)  # Encode string into json (read: dict)
    
    try:
        inGameUniqueKey = payLoad.get('gameUniqueKey')
        inFromPlayer = payLoad.get('fromPlayer')
        inToPlayer = payLoad.get('toPlayer')
        inDollarAmt = payLoad.get('dollarAmt')
    except KeyError:
        print('Missing Key Information in Submission')
        retVal['statusCode'] = 500
        retVal['body'] = json.dumps({ 'message': 'Data Missing', 'success': False })
    else:
        ledgerEntry['ledgerUUID'] = { 'S': str( uuid.uuid4() ) }
        ledgerEntry['gameUniqueKey'] = { 'S': inGameUniqueKey }
        ledgerEntry['transDate'] = { 'S': str(datetime.utcnow()) }
        ledgerEntry['fromPlayer'] = { 'S': inFromPlayer }
        ledgerEntry['toPlayer'] = { 'S' : inToPlayer }
        ledgerEntry['dollarAmt'] = { 'N' : inDollarAmt }
        
        try:
            dynamodb.put_item(
                TableName=table,
                Item=ledgerEntry
            )
        except Exception as e:
            print("Unhandled Error")
            print(e)
            retVal['statusCode'] = 500
            retVal['body'] = json.dumps(
                { 'message': 'Unhandled Error', 'success': False })
            return retVal
        else:
            print('Transaction Added to Ledger')
            retVal['body'] = json.dumps({ 'message': 'Entry Added', 'success': True })
            return retVal