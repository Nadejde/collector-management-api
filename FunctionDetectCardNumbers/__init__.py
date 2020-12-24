import logging
import requests
import azure.functions as func
from . import recognise
import json
from .. import database

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    collection_id = req.route_params.get('collection_id')
    collections = database.get_collections_container()

    collection = collections.query_items(
            query='SELECT * FROM collections r WHERE r.id = @id',
            parameters=[dict(name="@id", value=collection_id)],
            enable_cross_partition_query=True).next()
    collection_numbers = [i['number'] for i in collection['numbers']]
    numbers = []
    for f in req.files.values():
        filestream = f.stream
        filestream.seek(0)
        new_numbers = recognise.process_image(filestream, collection_numbers=collection_numbers)
        numbers = numbers + new_numbers

    numbers.sort()

    return func.HttpResponse(json.dumps(numbers), status_code=200)
