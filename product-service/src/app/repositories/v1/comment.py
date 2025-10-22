from .base import BaseRepository
from src.app.models.v1 import Comment, ProductVariation
from fastapi import HTTPException
from uuid import UUID
from sqlalchemy.orm import Session

class CommentRepository(BaseRepository[Comment]):
    def __init__(self, db: Session):
        super().__init__(Comment, db)

    def create(self, obj_in: dict) -> Comment:
        product_variation_id = obj_in.get("product_variation_id")
        if not product_variation_id:
            raise HTTPException(status_code=400, detail="product_variation_id is required")
        if not self.db.query(ProductVariation).filter(ProductVariation.id == product_variation_id).first():
            raise HTTPException(status_code=404, detail="ProductVariation not found")
        rating = obj_in.get("rating")
        if rating is not None and not (1 <= rating <= 5):
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        db_obj = Comment(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_by_variation(self, variation_id: UUID, skip: int = 0, limit: int = 100) -> list[Comment]:
        return self.db.query(Comment).filter(Comment.product_variation_id == variation_id).offset(skip).limit(limit).all()

    def delete(self, id: UUID) -> bool:
        db_obj = self.get(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False