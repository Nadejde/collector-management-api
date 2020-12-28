import logging
import azure.functions as func
from . import load_collection
from azure.cosmos import CosmosClient
import os

def main(req: func.HttpRequest, doc: func.Out[func.Document]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    client = CosmosClient(os.environ['COSMOS_ACCOUNT_URI'], credential=os.environ['COSMOS_ACCOUNT_KEY'])
    database = client.get_database_client('collectors')
    collections = database.get_container_client('collections')
    items = database.get_container_client('items')

    req_body = req.get_json()

    name = req_body.get('name').replace('/','-')
    numbers = req_body.get('numbers')
    manufacturer = req_body.get('manufacturer')
    collection_type = req_body.get('type')
    year = req_body.get('year')
    ebay = req_body.get('ebay')

    collection = load_collection.load(name, numbers, collection_type, year, manufacturer, ebay)
    collections.create_item(collection)

    for number in collection['numbers']:
        number['count'] = 0
        number['id'] = collection['name'] + " " + number['number']
        number['collection'] = collection['name']
        items.create_item(number)

    if collection['id']:
        return func.HttpResponse(collection['id'],status_code=200)
    else:
        return func.HttpResponse(
             "Collection not created",
             status_code=400
        )
