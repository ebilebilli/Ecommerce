from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from src.app.core.db import get_db
from src.app.core.db import SessionLocal
# Repositories
from src.app.repositories.v1.category import CategoryRepository
from src.app.repositories.v1.product import ProductRepository
from src.app.repositories.v1.product_variation import ProductVariationRepository
from src.app.repositories.v1.product_image import ProductImageRepository
from src.app.repositories.v1.comment import CommentRepository

# Schemas
from src.app.schemas.v1.category import CategoryCreate, Category
from src.app.schemas.v1.product import ProductCreate, Product
from src.app.schemas.v1.product_variation import ProductVariationCreate, ProductVariation
from src.app.schemas.v1.product_image import ProductImageCreate, ProductImage
from src.app.schemas.v1.comment import CommentCreate, Comment


router = APIRouter()

# Endpoints for Category
@router.post("/categories/", response_model=Category)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    return repo.create(category)

@router.get("/categories/", response_model=List[Category])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    return repo.get_all(skip, limit)

@router.get("/categories/{category_id}", response_model=Category)
def read_category(category_id: UUID, db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    category = repo.get(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.put("/categories/{category_id}", response_model=Category)
def update_category(category_id: UUID, category: CategoryCreate, db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    updated_category = repo.update(category_id, category)
    if not updated_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated_category

@router.delete("/categories/{category_id}")
def delete_category(category_id: UUID, db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    if not repo.delete(category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted"}

# Endpoints for Product
@router.post("/products/", response_model=Product)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    return repo.create(product)

@router.get("/products/", response_model=List[Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    return repo.get_all(skip, limit)

@router.get("/products/{product_id}", response_model=Product)
def read_product(product_id: UUID, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    product = repo.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/products/{product_id}", response_model=Product)
def update_product(product_id: UUID, product: ProductCreate, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    updated_product = repo.update(product_id, product)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@router.delete("/products/{product_id}")
def delete_product(product_id: UUID, db: Session = Depends(get_db)):
    repo = ProductRepository(db)
    if not repo.delete(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted"}

# Endpoints for ProductVariation
@router.post("/products/{product_id}/variations/", response_model=ProductVariation)
def create_product_variation(product_id: UUID, variation: ProductVariationCreate, db: Session = Depends(get_db)):
    repo = ProductVariationRepository(db)
    variation_data = variation.dict()
    variation_data["product_id"] = product_id
    return repo.create(variation_data)

@router.get("/products/{product_id}/variations/", response_model=List[ProductVariation])
def read_product_variations(product_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = ProductVariationRepository(db)
    variations = repo.get_all(skip, limit)
    return [v for v in variations if v.product_id == product_id]  # Filter by product_id

@router.get("/products/{product_id}/variations/{variation_id}", response_model=ProductVariation)
def read_product_variation(product_id: UUID, variation_id: UUID, db: Session = Depends(get_db)):
    repo = ProductVariationRepository(db)
    variation = repo.get(variation_id)
    if not variation or variation.product_id != product_id:
        raise HTTPException(status_code=404, detail="Variation not found")
    return variation

@router.put("/products/{product_id}/variations/{variation_id}", response_model=ProductVariation)
def update_product_variation(product_id: UUID, variation_id: UUID, variation: ProductVariationCreate, db: Session = Depends(get_db)):
    repo = ProductVariationRepository(db)
    updated_variation = repo.update(variation_id, variation.dict())
    if not updated_variation or updated_variation.product_id != product_id:
        raise HTTPException(status_code=404, detail="Variation not found")
    return updated_variation

@router.delete("/products/{product_id}/variations/{variation_id}")
def delete_product_variation(product_id: UUID, variation_id: UUID, db: Session = Depends(get_db)):
    repo = ProductVariationRepository(db)
    if not repo.delete(variation_id) or not repo.get(variation_id) or repo.get(variation_id).product_id != product_id:
        raise HTTPException(status_code=404, detail="Variation not found")
    return {"message": "Variation deleted"}

# Endpoints for ProductImage
@router.post("/products/{product_id}/variations/{variation_id}/images/", response_model=ProductImage)
def create_product_image(product_id: UUID, variation_id: UUID, image: ProductImageCreate, db: Session = Depends(get_db)):
    repo = ProductImageRepository(db)
    image_data = image.dict()
    image_data["product_variation_id"] = variation_id
    return repo.create(image_data)

@router.get("/products/{product_id}/variations/{variation_id}/images/", response_model=List[ProductImage])
def read_product_images(product_id: UUID, variation_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = ProductImageRepository(db)
    return repo.get_by_variation(variation_id, skip, limit)

@router.delete("/products/{product_id}/variations/{variation_id}/images/{image_id}")
def delete_product_image(product_id: UUID, variation_id: UUID, image_id: UUID, db: Session = Depends(get_db)):
    repo = ProductImageRepository(db)
    if not repo.delete(image_id):
        raise HTTPException(status_code=404, detail="Image not found")
    return {"message": "Image deleted"}

# Endpoints for Comment
@router.post("/products/{product_id}/variations/{variation_id}/comments/", response_model=Comment)
def create_comment(product_id: UUID, variation_id: UUID, comment: CommentCreate, db: Session = Depends(get_db)):
    repo = CommentRepository(db)
    comment_data = comment.dict()
    comment_data["product_variation_id"] = variation_id
    return repo.create(comment_data)

@router.get("/products/{product_id}/variations/{variation_id}/comments/", response_model=List[Comment])
def read_comments(product_id: UUID, variation_id: UUID, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    repo = CommentRepository(db)
    return repo.get_by_variation(variation_id, skip, limit)