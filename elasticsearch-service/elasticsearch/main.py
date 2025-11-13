from fastapi import FastAPI, Query, APIRouter
from .documents import create_index, INDEX_NAME, ELASTIC
from threading import Thread
from .consumer import start_consumer
import asyncio


router = APIRouter(prefix='/elasticsearch/api', tags=['ElasticSearch'])
app = FastAPI()


@app.on_event('startup')
def startup_event():
    create_index()
    Thread(target=start_consumer, daemon=True).start()


@app.get('shop/search/')
async def search_shops(query: str = Query(..., description='Shop name query')):
    result = await ELASTIC.search(
        index=INDEX_NAME,
        query={
            'match': {
                'name': {
                    'query': query,
                    'fuzziness': 'AUTO'  
                }
            }
        },
        size=10
    )
    hits = result['hits']['hits']
    return [hit['_source'] for hit in hits]