from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models import Wishlist, WishlistCreate, WishlistResponse

router = APIRouter()

@router.post("/wishlist", response_model=WishlistResponse, status_code=status.HTTP_201_CREATED)
def add_to_wishlist(
    wishlist: WishlistCreate, 
    session: Session = Depends(get_session)
):
    """Add product to user's wishlist"""
    
    # Check if already exists
    existing = session.exec(
        select(Wishlist).where(
            Wishlist.user_id == wishlist.user_id,
            Wishlist.product_variation_id == wishlist.product_variation_id,
            Wishlist.shop_id == wishlist.shop_id
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product already in wishlist for this shop"
        )
    
    # Create new wishlist item
    db_wishlist = Wishlist(**wishlist.dict())
    session.add(db_wishlist)
    session.commit()
    session.refresh(db_wishlist)
    
    return db_wishlist

@router.get("/wishlist/{user_id}", response_model=list[WishlistResponse])
def get_user_wishlist(user_id: int, session: Session = Depends(get_session)):
    """Get user's wishlist"""
    wishlist_items = session.exec(
        select(Wishlist).where(Wishlist.user_id == user_id)
    ).all()
    
    return wishlist_items

@router.delete("/wishlist/{user_id}/{product_variation_id}/{shop_id}")
def remove_from_wishlist(
    user_id: int,
    product_variation_id: int,
    shop_id: int,
    session: Session = Depends(get_session)
):
    """Remove product from wishlist"""
    
    wishlist_item = session.exec(
        select(Wishlist).where(
            Wishlist.user_id == user_id,
            Wishlist.product_variation_id == product_variation_id,
            Wishlist.shop_id == shop_id
        )
    ).first()
    
    if not wishlist_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wishlist item not found"
        )
    
    session.delete(wishlist_item)
    session.commit()
    
    return {"message": "Item removed from wishlist successfully"}

@router.get("/wishlist/count/{user_id}")
def get_wishlist_count(user_id: int, session: Session = Depends(get_session)):
    """Get count of items in user's wishlist"""
    count = session.exec(
        select(Wishlist).where(Wishlist.user_id == user_id)
    ).all()
    
    return {"user_id": user_id, "wishlist_count": len(count)}