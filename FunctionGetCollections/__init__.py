import logging
import azure.functions as func
from .. import database
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    collections = database.get_collections_container()

    items = list(collections.query_items(
        query='SELECT items.id, items.name, items.type, items.year, items.manufacturer FROM items',
        enable_cross_partition_query=True))

    logging.info(items)

    return func.HttpResponse(
        json.dumps(items),
        status_code=200
    )
