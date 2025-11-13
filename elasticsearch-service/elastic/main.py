from fastapi import FastAPI, Query, APIRouter
from .documents import create_index, INDEX_NAME, ELASTIC


router = APIRouter(prefix='/api/elasticsearch', tags=['ElasticSearch'])
app = FastAPI(title="Elasticsearch Service API", version="1.0.0")


@router.get('/search/')
def search_shops(query: str = Query(..., description='Shop name query')):
    result = ELASTIC.search(
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



app.include_router(router)


@app.on_event('startup')
def startup_event():
    try:
        create_index()
        print("Index created or already exists")
    except Exception as e:
        print(f"Warning: Could not create index: {e}")