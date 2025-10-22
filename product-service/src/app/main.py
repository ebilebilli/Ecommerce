from fastapi import FastAPI

from src.app.api.v1.routes import router

app = FastAPI(
    title="Product Service",
    version="1.0.0",
    description="Manages products, categories, variations, and images.",
    debug=True,
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Product Service is running 🚀"}
