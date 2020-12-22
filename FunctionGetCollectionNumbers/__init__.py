import logging
from .. import database
import json
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    items_container = database.get_items_container()
    collection_id = req.route_params.get('collection_id')

    items = list(items_container.query_items(
        query='SELECT r.number, r.text, r.count, r.id FROM items r WHERE r.collection = @collection',
        parameters=[dict(name="@collection", value=collection_id)],
        enable_cross_partition_query=True))

    logging.info(items)

    return func.HttpResponse(
        json.dumps(items),
        status_code=200
    )