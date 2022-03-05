import json
from decimal import Decimal
def create_table1(dynamodb,tablename,hashname,hashtype,sortname,sorttype,readcapacity,writecapacity):
    readcapacity=int(readcapacity)
    writecapacity=int(writecapacity)
    hashtype=str.upper(hashtype)
    sorttype=str.upper(sorttype)
    dynamodb.create_table(
        TableName=tablename,
        KeySchema=[
            {
                'AttributeName': hashname,
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': sortname,
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': hashname,
                'AttributeType': hashtype
            },
            {
                'AttributeName': sortname,
                'AttributeType': sorttype
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': readcapacity,
            'WriteCapacityUnits': writecapacity
        }
    )


def create_table2(dynamodb,tablename,hashname,hashtype,readcapacity,writecapacity):
    readcapacity=int(readcapacity)
    writecapacity=int(writecapacity)
    hashtype=str.upper(hashtype)
    dynamodb.create_table(
        TableName=tablename,
        KeySchema=[
            {
                'AttributeName': hashname,
                'KeyType': 'HASH'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': hashname,
                'AttributeType': hashtype
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': readcapacity,
            'WriteCapacityUnits': writecapacity
        }
    )

def load_table(dynamodb,tablename,files):
    table = dynamodb.Table(tablename)
    for single_file in files:
            single_file=json.dumps(single_file)
            single_file=json.loads(single_file,parse_float=Decimal)
            table.put_item(Item=single_file)
    return True

def update_item(dynamodb,tablename,hashname,hashvalue,updatename,updatevalue,sortname=None,sortvalue=None):
    table=dynamodb.Table(tablename)
    updateexpression='set '
    attributevalues={}
    for i in range(0,len(updatename)):
            naming1=updatename[i].replace(".","")
            updateexpression+=updatename[i]+' = :'+naming1+','
            attributevalues[':'+naming1]=updatevalue[i]
    updateexpression=updateexpression[:len(updateexpression)-1]
    print(updateexpression) 
    if sortname is None:
        key_args={
            hashname: hashvalue
        }
    else:
        key_args={
            hashname: hashvalue,
            sortname: sortvalue
        }
    table.update_item(
            Key=key_args,
            UpdateExpression=updateexpression,
            ExpressionAttributeValues=attributevalues,
            ReturnValues="UPDATED_NEW"
        )
   
def view_table_full1(dynamodb,tablename):
    table=dynamodb.Table(tablename)
    result=list()
    scan_args=dict()
    done=False
    start_key=False
    while not done:
        if start_key:
            scan_args['ExclusiveStartKey']=start_key
        resp=table.scan(**scan_args)
        datas=resp['Items']
        for data in datas:
            result.append(data)
        start_key = resp.get('LastEvaluatedKey', None)
        if start_key is None:
            done=True
    return result

def is_list(data,name):
    if name.find(".")>0:
        res=name.split(".")
        if type(data[res[0]].get(res[1])) is list:
            return True

def filter_details(dynamodb,tablename,filtername,filtervalues,keyname=None,keyvalues=None):
    table=dynamodb.Table(tablename)
    result=list()
    totalresp=table.scan(Limit=1)
    totalresp=totalresp['Items']
    if keyname==None and keyvalues==None:
        keyexpression,filterexpression,attributenames,attributevalues=filter_details_helper_query(filtername,filtervalues,totalresp[0])
        filterexpression=filterexpression[:len(filterexpression)-4]
        scan_args={
            'FilterExpression':filterexpression,
            'ExpressionAttributeValues':attributevalues
        }
        done=False
        start_key=False
        while not done:
            if start_key:
                scan_args['ExclusiveStartKey']=start_key
            resp=table.scan(**scan_args)
            datas=resp['Items']
            for data in datas:           
                result.append(data)
            start_key = resp.get('LastEvaluatedKey', None)
            if start_key is None:
                done=True
        return result
    else:
        keyexpression,filterexpression,attributenames,attributevalues=filter_details_helper_query(filtername,filtervalues,totalresp[0],keyname,keyvalues)
        keyexpression=keyexpression[:len(keyexpression)-4]
        if (not filterexpression):
            resp=table.query(KeyConditionExpression=keyexpression,ExpressionAttributeNames=attributenames,ExpressionAttributeValues=attributevalues,Limit=10)
        else:
            filterexpression=filterexpression[:len(filterexpression)-4]
            resp=table.query(KeyConditionExpression=keyexpression,FilterExpression=filterexpression,ExpressionAttributeNames=attributenames,ExpressionAttributeValues=attributevalues,Limit=10)
        datas=resp['Items']
    for data in datas:
        result.append(data)
    return result

def filter_details_helper_query(filtername,filtervalues,data,keynames=None,keyvalues=None):
        attributenames={}
        attributevalues={}
        keyexpression=""
        filterexpression=""
        if keynames!=None:
            for i in range(0,len(keynames)):
                keyexpression+='#'+keynames[i]+' = :'+keynames[i]+' and '
                attributenames['#'+keynames[i]]=keynames[i]
                attributevalues[':'+keynames[i]]=keyvalues[i]
        for i in range(0,len(filtername)):
            naming1=filtername[i].replace(".","")
            if is_list(data,filtername[i]):
                filterexpression+='contains('+filtername[i]+', :'+naming1+') and '
                attributevalues[':'+naming1]=filtervalues[i]
            else:
                filterexpression+=filtername[i]+' = :'+naming1+' and '
                attributevalues[':'+naming1]=filtervalues[i]
        return keyexpression,filterexpression,attributenames,attributevalues