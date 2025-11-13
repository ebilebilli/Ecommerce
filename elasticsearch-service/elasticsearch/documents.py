import os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv


load_dotenv()

ELASTIC_HOST = os.getenv('ELASTIC_HOST', 'http://elasticsearch:9200')
ELASTIC_USERNAME = os.getenv('ELASTIC_USERNAME', 'elastic')
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD', '')

# Create Elasticsearch client with authentication
ELASTIC = Elasticsearch(
    [ELASTIC_HOST],
    basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD) if ELASTIC_PASSWORD else None,
    verify_certs=False,
    ssl_show_warn=False
)

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