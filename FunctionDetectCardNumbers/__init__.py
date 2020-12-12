import logging
import requests
import azure.functions as func
from . import recognise
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    collection_id = req.route_params.get('collection_id')
    numbers = []
    for f in req.files.values():
        filestream = f.stream
        filestream.seek(0)
        new_numbers = recognise.process_image(filestream, collection_id=collection_id)
        numbers = numbers + new_numbers

    return func.HttpResponse(json.dumps(numbers), status_code=200)
