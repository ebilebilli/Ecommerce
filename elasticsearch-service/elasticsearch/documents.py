import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv


load_dotenv()

ELASTIC = os.getenv('ELASTIC_HOST')
INDEX_NAME = 'shops'


def create_index():
    if not ELASTIC.indices.exists(index=INDEX_NAME):
        ELASTIC.indices.create(
            index=INDEX_NAME,
            body={
                "mappings": {
                    "properties": {
                        "name": {"type": "text", "analyzer": "standard"}
                    }
                }
            }
        )