from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal


def add_player(event, context):
    dynamodb = boto3.client('dynamodb')
    table = 'player'
    item = {} # will be used to track what we put in DynamoDB
    payLoad = event['body'] # API Gateway passes unencoded json (read: string) in body
    payLoad = json.loads(payLoad) # Encode string into json (read: dict)

    if 'email' in payLoad:
        inEmail = payLoad['email']
        item['email'] = {'S': payLoad['email']}
    else: # kill the whole thing if we don't get a club name
        print('No Email Passed')
        print(payLoad)

    if 'fullName' in payLoad:
        item['fullName'] = {'S': payLoad['fullName']}

    if 'nickName' in payLoad:
        item['nickName'] = {'S': payLoad['nickName']}

    print('Trying to add: ' + inEmail)

    try:
        response = dynamodb.put_item(
            TableName=table, 
            Item=item,
            ConditionExpression="attribute_not_exists(email)"
        )
    except Exception as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            print(inEmail + ' already exists in table ' + table)

            return {
                "isBase64Encoded": False,
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": '*',
                    'Access-Control-Allow-Credentials': True
                },
                'body': json.dumps({
                    'message': 'Email already exists',
                    'success': False
                })
            }
        else:
            print(e.response['Error']['Code'])
    else:
        print("Player Created")
    
        # This allows the API to not return 502 Bad Gateway
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": '*',
                'Access-Control-Allow-Credentials': True
            },
            'body': json.dumps({
                'message': 'Player Added!',
                'success': True
            })
        }

def get_player(event, context):
    dynamodb = boto3.client('dynamodb')
    table = 'player'

    if (event["queryStringParameters"] is not None): # verify we got query strings
        qsParams = event["queryStringParameters"]

        if 'email' in qsParams:
            try:
                response = dynamodb.query(
                    TableName = table,
                    Key = {
                        'email' : {'S' : str(qsParams['email'])}
                    }
                )
            except Exception as e:
                #print(e.response['Error']['Message'])
                print(e.args)

                return {
                    "isBase64Encoded": False,
                    "statusCode": 200,
                    "headers": {
                        "Access-Control-Allow-Origin": '*',
                        'Access-Control-Allow-Credentials': True
                    },
                    'body': json.dumps({
                        'player': {},
                        'success': False
                    })
                }
            else:
                print("Player Returned")
                player = response['Item']

                # This allows the API to not return 502 Bad Gateway
                return {
                    "isBase64Encoded": False,
                    "statusCode": 200,
                    "headers": {
                        "Access-Control-Allow-Origin": '*',
                        'Access-Control-Allow-Credentials': True
                    },
                    'body': json.dumps({
                        'player': player,
                        'success': True
                    })
                }
    
def update_player(event, context):
    dynamodb = boto3.client('dynamodb')
    table = 'player'
    payLoad = event['body'] # API Gateway passes unencoded json (read: string) in body
    payLoad = json.loads(payLoad) # Encode string into json (read: dict)

    # Get the item first
    if 'email' in payLoad:
        print('Looking for player ' + payLoad['email'])
        try:
            response = dynamodb.get_item(
                TableName = table,
                Key = {
                    'email' : {'S' : str(payLoad['email'])}
                }
            )
        except Exception as e:
            print('Not matching player found')
            print(e.args)
            return {
                "isBase64Encoded": False,
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": '*',
                    'Access-Control-Allow-Credentials': True
                },
                'body': json.dumps({
                    'message': 'Player could not be found',
                    'success': False
                })
            }
        else:
            print('Player was found')
            player = response['Item']

            if 'fullName' in payLoad:
                player['fullName'] = {'S': payLoad['fullName'] }

            if 'nickName' in payLoad:
                player['nickName'] = {'S': payLoad['nickName'] }

            try:
                print('Trying to update player')
                dynamodb.put_item(TableName=table, Item=player)
            except Exception as e:
                print('Player failed to update')
                print(e.args)
                return {
                    "isBase64Encoded": False,
                    "statusCode": 200,
                    "headers": {
                        "Access-Control-Allow-Origin": '*',
                        'Access-Control-Allow-Credentials': True
                    },
                    'body': json.dumps({
                        'message': 'Player could not be updated',
                        'success': False
                    })
                }
            else:
                print("Player Updated")
                return {
                    "isBase64Encoded": False,
                    "statusCode": 200,
                    "headers": {
                        "Access-Control-Allow-Origin": '*',
                        'Access-Control-Allow-Credentials': True
                    },
                    'body': json.dumps({
                        'message': 'Player Updated',
                        'success': True
                    })
                }
    else:
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": '*',
                'Access-Control-Allow-Credentials': True
            },
            'body': json.dumps({
                'message': 'Email was not submitted',
                'success': False
            })
        }