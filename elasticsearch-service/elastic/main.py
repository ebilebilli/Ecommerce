from fastapi import FastAPI, Query, APIRouter
from .documents import create_indices, SHOP_INDEX_NAME, PRODUCT_INDEX_NAME, ELASTIC


router = APIRouter(prefix='/api/elasticsearch', tags=['ElasticSearch'])
app = FastAPI(title="Elasticsearch Service API", version="1.0.0")


@router.get('/search/')
def search_all(
    query: str = Query(..., description='Search query for shops and products'),
    size: int = Query(10, description='Number of results per type')
):
    """
    Unified search endpoint that searches across shops and products
    """
    results = {
        'shops': [],
        'products': []
    }
    
    # Search shops
    try:
        shop_result = ELASTIC.search(
            index=SHOP_INDEX_NAME,
            query={
                'match': {
                    'name': {
                        'query': query,
                        'fuzziness': 'AUTO'  
                    }
                }
            },
            size=size
        )
        results['shops'] = [hit['_source'] for hit in shop_result['hits']['hits']]
    except Exception as e:
        print(f"Error searching shops: {e}")
    
    # Search products
    try:
        product_result = ELASTIC.search(
            index=PRODUCT_INDEX_NAME,
            query={
                'multi_match': {
                    'query': query,
                    'fields': ['title^2', 'about'],
                    'fuzziness': 'AUTO'
                }
            },
            size=size
        )
        results['products'] = [hit['_source'] for hit in product_result['hits']['hits']]
    except Exception as e:
        print(f"Error searching products: {e}")
    
    return results


@router.get('/shop/{shop_id}/products/')
def get_products_by_shop(
    shop_id: str,
    size: int = Query(100, description='Number of results to return')
):
    """
    Get all products for a specific shop by shop_id
    Returns only products
    """
    if not shop_id or shop_id.strip() == '':
        return {
            'products': [],
            'total': 0,
            'error': 'shop_id is required'
        }
    
    try:
        # Use term query for exact match on keyword field
        # term query works with keyword fields and does exact match
        result = ELASTIC.search(
            index=PRODUCT_INDEX_NAME,
            query={
                'bool': {
                    'must': [
                        {
                            'term': {
                                'shop_id': shop_id
                            }
                        },
                        {
                            'exists': {
                                'field': 'shop_id'
                            }
                        }
                    ]
                }
            },
            size=size
        )
        products = [hit['_source'] for hit in result['hits']['hits']]
        return {
            'products': products,
            'total': result['hits']['total']['value']
        }
    except Exception as e:
        print(f"Error searching products by shop_id: {e}")
        # Fallback: Try simple term query
        try:
            result = ELASTIC.search(
                index=PRODUCT_INDEX_NAME,
                query={
                    'term': {
                        'shop_id': shop_id
                    }
                },
                size=size
            )
            products = [hit['_source'] for hit in result['hits']['hits']]
            return {
                'products': products,
                'total': result['hits']['total']['value']
            }
        except Exception as e2:
            return {
                'products': [],
                'total': 0,
                'error': str(e2)
            }


app.include_router(router)


@app.on_event('startup')
def startup_event():
    try:
        create_indices()
        print("Indices created or already exist")
    except Exception as e:
        print(f"Warning: Could not create indices: {e}")