import logging
import os
import azure.functions as func
from azure.cosmos import CosmosClient

def get_numbers_to_add(collection, input_numbers):
    numbers_to_add = {}
    for number in collection['numbers']:
        if number['number'] in input_numbers:
            logging.info(number)
            numbers_to_add[number['number']] = number
            numbers_to_add[number['number']]['count'] = input_numbers.count(number['number'])
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
        numbers = req_body.get('numbers')
        collection = collections.query_items(
            query='SELECT * FROM collections r WHERE r.id = @id',
            parameters=[dict(name="@id", value=collection_id)],
            enable_cross_partition_query=True).next()
        
        numbers_to_add = get_numbers_to_add(collection, numbers)
        add_number_to_items_container(items, collection_id, numbers_to_add)
            
            
    return func.HttpResponse("OK", status_code=200)
 
