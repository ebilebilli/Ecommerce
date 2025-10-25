from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select
from app.database import get_session
from app.models import Wishlist, WishlistCreate, WishlistResponse
from app.product_client import product_client
from app.shop_client import shop_client

router = APIRouter()

@router.post("/wishlist", response_model=WishlistResponse, status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    wishlist: WishlistCreate, 
    session: Session = Depends(get_session)
):
    if wishlist.product_variation_id:
        product_data = await product_client.get_product_data_by_variation_id(wishlist.product_variation_id)
        if not product_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product variation not found in Product Service"
            )
        existing = session.exec(
            select(Wishlist).where(
                Wishlist.user_id == wishlist.user_id,
                Wishlist.product_variation_id == wishlist.product_variation_id
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product already in wishlist"
            )
        db_wishlist = Wishlist(
            user_id=wishlist.user_id,
            product_variation_id=wishlist.product_variation_id
        )
    
    elif wishlist.shop_id:
        shop_data = await shop_client.get_shop_data(wishlist.shop_id)
        if not shop_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Shop not found in Shop Service"
            )
        existing = session.exec(
            select(Wishlist).where(
                Wishlist.user_id == wishlist.user_id,
                Wishlist.shop_id == wishlist.shop_id
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Shop already in wishlist"
            )
        db_wishlist = Wishlist(
            user_id=wishlist.user_id,
            shop_id=wishlist.shop_id
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either product_variation_id or shop_id must be provided"
        )

    session.add(db_wishlist)
    session.commit()
    session.refresh(db_wishlist)
    return db_wishlist


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