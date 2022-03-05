from decimal import Decimal
import os
import json
import boto3
import traceback
from botocore.exceptions import ClientError
from jinja2 import Environment, FileSystemLoader
from layer import *

def lambda_handler(event, context):

    region = os.environ['REGION']
    aws_environment = os.environ['AWSENV']
    dev_environment = os.environ['DEVENV']

    # Check if executing locally or on AWS, and configure DynamoDB connection accordingly.
    if aws_environment == "AWS_SAM_LOCAL":
        # SAM LOCAL
        if dev_environment == "OSX":
            dynamodb = boto3.resource('dynamodb', endpoint_url="http://docker.for.mac.localhost:8000/")

        elif dev_environment == "Windows":
            dynamodb = boto3.resource('dynamodb', endpoint_url="http://docker.for.windows.localhost:8000/")

        else:
            dynamodb = boto3.resource('dynamodb', endpoint_url="http://127.0.0.1:8000")
    else:
        dynamodb = boto3.resource('dynamodb', region_name=region)


    # Print statement for debugging.
    #print(event)
    
    # Load body JSON for processing
    try:
        if event['body']:
            bodydict = json.loads(event['body'])
        tablename=event['pathParameters']['tablename']
    except:
        return {'statusCode': 400, 'body': 'malformed JSON'}

    if event['httpMethod'] == 'GET':
        try:
            env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates"), encoding="utf8"))
            if bodydict.get('filtername') and bodydict.get('keyname'):
                queriesname=bodydict['keyname']
                queriesvalues=bodydict['keyvalues']
                queriesname1=bodydict['filtername']
                queriesvalues1=bodydict['filtervalues']
                result=filter_details(dynamodb,tablename,queriesname1,queriesvalues1,queriesname,queriesvalues)
            elif bodydict.get('filtername'):
                queriesname=bodydict['filtername']
                queriesvalues=bodydict['filtervalues']
                result=filter_details(dynamodb,tablename,queriesname,queriesvalues)
            else:
                result=view_table_full1(dynamodb,tablename)
            template = env.get_template("fullView.html")
            html = template.render(
                    result=result
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            return {'statusCode': 400, 'body': e.response['Error']['Message']}
        return {'statusCode':200,
                'body':html, 
                'headers': {
                    'Content-Type': 'text/html',
                }}

    elif event['httpMethod'] == 'POST':
        print("In POST method")

        try:
            if not bodydict["HashName"]:
                return {'statusCode': 400, 'body': 'missing hash name.'}
            if not(bodydict["HashType"]):
                return {'statusCode': 400, 'body': 'missing hash type.'}
            if not(bodydict["readcapacity"]):
                return {'statusCode': 400, 'body': 'missing readcapacity.'}
            if not(bodydict["writecapacity"]):
                return {'statusCode': 400, 'body': 'missing writecapacity.'}     
            hashname=bodydict['HashName']
            hashtype=bodydict['HashType']
            readcapacity=bodydict['readcapacity']
            writecapacity=bodydict['writecapacity']
            if bodydict['SortName']==None:
                print("No Sort Key")
                create_table2(dynamodb,tablename,hashname,hashtype,readcapacity,writecapacity)
            else:
                sortname=bodydict['SortName']
                sorttype=bodydict['SortType']
                create_table1(dynamodb,tablename,hashname,hashtype,sortname,sorttype,readcapacity,writecapacity)
        except ClientError as e:
            print(e.response['Error']['Message'])
            return {'statusCode': 400, 'body': e.response['Error']['Message']}
        else:
            return {'statusCode': 200, 'body': "Table Created Successfully"}

    elif event['httpMethod'] == 'DELETE':
        try:
           table=dynamodb.Table(tablename)
           table.delete()
        except:
            traceback.print_exc()
            return {'statusCode': 400, 'body': 'Error in Deleting Table.'}
        else:
            return {'statusCode': 200, 'body': "Deleted Successfully"} 


    elif event['httpMethod'] == 'PUT':
        try:
            load_table(dynamodb,tablename,bodydict)
        except ClientError as e:
            print(e.response['Error']['Message'])
            return {'statusCode': 400, 'body': e.response['Error']['Message']}
        else:
            return {'statusCode':200,'body':'Added Values successfully'}
    
    elif event['httpMethod'] == 'PATCH':
        hashname=bodydict['hashname']
        hashvalue=bodydict['hashvalue']
        updatename=bodydict['updatename']
        updatevalue=bodydict['updatevalue']
        if bodydict['sortname'] is None:
            try:
                update_item(dynamodb,tablename,hashname,hashvalue,updatename,updatevalue)
            except ClientError as e:
                print(e.response['Error']['Message'])
                return {'statusCode': 400, 'body': e.response['Error']['Message']}
        else:
            try:
                update_item(dynamodb,tablename,hashname,hashvalue,updatename,updatevalue,bodydict['sortname'],bodydict['sortvalue'])
            except ClientError as e:
                print(e.response['Error']['Message'])
                return {'statusCode': 400, 'body': e.response['Error']['Message']}  
        return {'statusCode':200,'body':'Updated Values successfully'}
            
        



