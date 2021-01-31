import logging
from .. import database
import json
import azure.functions as func


def search_in_collection(items, numbers):
    found = []
    missing = []

    for item in items:
        if item['number'] in numbers:
            if item['count'] > 0:
                found.append(item)
            else: 
                missing.append(item)
    
    return found, missing
    

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    items_container = database.get_items_container()
    collection_id = req.route_params.get('collection_id')
    req_body = req.get_json()
    
    numbers = req_body.get('numbers', "")
    numbers = numbers.replace(' ',',')
    numbers = numbers.replace('\n',',')
    numbers = numbers.split(',')

    items = list(items_container.query_items(
        query='SELECT r.number, r.text, r.count, r.id FROM items r WHERE r.collection = @collection',
        parameters=[dict(name="@collection", value=collection_id)],
        enable_cross_partition_query=True))

    found, missing = search_in_collection(items, numbers)

    if (len(found) == 0): #try a different strategy for index
        new_numbers = []
        numbers = req_body.get('numbers', "")
        for line in numbers.splitlines():
            index = (line.split('-')[0]).replace(' ', '')
            rest = line.split('-')[1]
            for number in rest.split(','):
                new_numbers.append(index + number.replace(' ', ''))
            
        found, missing = search_in_collection(items, new_numbers)



    return func.HttpResponse(
        json.dumps({'found': found, 'missing': missing}),
        status_code=200
    )
