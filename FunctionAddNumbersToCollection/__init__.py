import logging
import os
import azure.functions as func
from azure.cosmos import CosmosClient

def get_numbers_to_add(collection, input_numbers):
    numbers_to_add = {}
    for number in collection['numbers']:
        if number['number'] in input_numbers:
            numbers_to_add[number['number']] = number
            numbers_to_add[number['number']]['count'] = input_numbers.count(number['number'])
            numbers_to_add[number['number']]['collection'] = collection['name']
    
    return numbers_to_add

def get_numbers_to_add_with_prefix(collection, input):
    input_numbers = []
    numbers_to_add = {}
    for line in input.splitlines():
        prefix = line.split(' ')[0]
        for number in (line.split(' ')[1]).split(','):
            input_numbers.append(prefix + number)

    for number in collection['numbers']:
        if number['number'] in input_numbers:
            numbers_to_add[number['number']] = number
            numbers_to_add[number['number']]['count'] = input_numbers.count(number['number'])
            numbers_to_add[number['number']]['collection'] = collection['name']
    
    return numbers_to_add

def get_numbers_to_add_from_csv(collection, csv):
    input_numbers = {}
    for line in csv.splitlines():
        number = (line.strip().split(',')[0]).replace(' ', '')
        count = int((line.strip().split(',')[1]).strip(' '))
        input_numbers[number] = count
    numbers_to_add = {}
    for number in collection['numbers']:
        if number['number'] in input_numbers.keys():
            numbers_to_add[number['number']] = number
            numbers_to_add[number['number']]['count'] = input_numbers[number['number']]
            numbers_to_add[number['number']]['collection'] = collection['name']
    
    return numbers_to_add

def add_number_to_items_container(container, collection_id, numbers):
    items = container.query_items(
        query='SELECT * FROM items r WHERE r.collection = @collection',
        parameters=[dict(name="@collection", value=collection_id)],
        enable_cross_partition_query=True)
    for item in items:
        if item['number'] in numbers:
            item['count'] = item['count'] + numbers[item['number']]['count']
            container.replace_item(item=item, body=item)

def remove_numbers_from_items_container(container, collection_id, numbers):
    items = container.query_items(
        query='SELECT * FROM items r WHERE r.collection = @collection',
        parameters=[dict(name="@collection", value=collection_id)],
        enable_cross_partition_query=True)
    for item in items:
        if item['number'] in numbers:
            item['count'] = item['count'] - numbers[item['number']]['count']
            container.replace_item(item=item, body=item)

def clear_collection(container, collection_id):
    items = container.query_items(
        query='SELECT * FROM items r WHERE r.collection = @collection',
        parameters=[dict(name="@collection", value=collection_id)],
        enable_cross_partition_query=True)
    for item in items:
        item['count'] = 0
        container.replace_item(item=item, body=item)
        

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    client = CosmosClient(os.environ['COSMOS_ACCOUNT_URI'], credential=os.environ['COSMOS_ACCOUNT_KEY'])
    database = client.get_database_client('collectors')
    collections = database.get_container_client('collections')
    items = database.get_container_client('items')

    try:
        req_body = req.get_json()
    except ValueError:
        pass
    else:
        collection_id = req.route_params.get('collection_id')
        numbers = req_body.get('numbers', [])
        remove_numbers = req_body.get('remove_numbers', [])
        numbers_csv = req_body.get('numbers_csv','')
        numbers_prefix = req_body.get('numbers_prefix','')
        clear_colection = req_body.get('clear', False)
        collection = collections.query_items(
            query='SELECT * FROM collections r WHERE r.id = @id',
            parameters=[dict(name="@id", value=collection_id)],
            enable_cross_partition_query=True).next()
        
        if(clear_colection):
            clear_collection(items , collection_id)

        if(len(numbers) > 0):
            numbers_to_add = get_numbers_to_add(collection, numbers)
            add_number_to_items_container(items , collection_id, numbers_to_add)

        if(len(remove_numbers) > 0):
            numbers_to_remove = get_numbers_to_add(collection, remove_numbers)
            remove_numbers_from_items_container(items , collection_id, numbers_to_remove)

        if(numbers_csv != ''):
            numbers_to_add = get_numbers_to_add_from_csv(collection, numbers_csv)
            add_number_to_items_container(items , collection_id, numbers_to_add)

        if(numbers_prefix != ''):
            numbers_to_add = get_numbers_to_add_with_prefix(collection, numbers_prefix)
            add_number_to_items_container(items , collection_id, numbers_to_add)
                       
    return func.HttpResponse("OK", status_code=200)
 
