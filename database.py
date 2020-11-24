from azure.cosmos import CosmosClient
import os

client = CosmosClient(os.environ['COSMOS_ACCOUNT_URI'], credential=os.environ['COSMOS_ACCOUNT_KEY'])
database = client.get_database_client('collectors')
collections = database.get_container_client('collections')
items = database.get_container_client('items')

def get_collections_container():
    return collections

def get_items_container():
    return items