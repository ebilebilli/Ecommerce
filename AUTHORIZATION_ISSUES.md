# 🚨 Authorization & Security Issues - Təhlükəsizlik Problemləri

## 📋 Problem Özəti

Sistemdə **Authentication** var amma **Authorization** tam deyil. Yəni:
- ✅ User login ola bilər (token validdir)
- ❌ User özünə aid olmayan data-ya çata bilər

---

## 🔴 Kritik Problemlər

### **1. ShopCart Service - Cart Ownership Check YOXDUR**

**Problem:** User başqa birinin cart-ına item əlavə edə və ya dəyişdirə bilər.

#### **🎯 Problemli Endpoint-lər:**

**Line 42-50:** `add_item`
```python
@router.post("/{cart_id}/items/{product_var_id}", response_model=schemas.CartItemRead)
async def add_item(cart_id: int, product_var_id: str, item: schemas.CartItemCreate, db: Session = Depends(db.get_db)):
    # ❌ cart_id user-a aididirmi yoxlamır!
    return crud.add_item_to_cart(db, product_var_id, cart_id, item)
```

**Nəticə:**
```bash
# User A-nın cart_id = 1
# User B göndərə bilər:
POST /shopcart/1/items/123
Headers: { X-User-Id: "user-b-uuid" }  # ❌ User B başqasının cart-ına item əlavə edir!
```

**Line 54-59:** `update_cart_item`
```python
@router.put("/{cart_id}/items/{item_id}")
def update_cart_item(cart_id: int, item_id: int, item: schemas.CartItemUpdate, db: Session = Depends(db.get_db)):
    # ❌ Bu cart user-a aididirmi yoxlamır!
    updated_item = crud.update_cart(db, item_id, cart_id, item)
```

**Line 63-68:** `delete_cart_item`
```python
@router.delete("/{cart_id}/items/{item_id}")
def delete_cart_item(cart_id: int, item_id: int, db: Session = Depends(db.get_db)):
    # ❌ Bu cart user-a aididirmi yoxlamır!
    deleted_item = crud.delete_cart_item(db, item_id, cart_id)
```

---

### **2. Product Service - Product Ownership Check Tam De İL**

**Line 96-102:** `update_product`
```python
@router.put("/products/{product_id}", response_model=Product)
def update_product(product_id: UUID, product: ProductCreate, request: Request, db: Session = Depends(get_db)):
    # ❌ Authorization yoxlaması yoxdur!
    updated_product = repo.update(product_id, product)
    return updated_product
```

**Line 122-127:** `delete_product`
```python
@router.delete("/products/{product_id}")
def delete_product(product_id: UUID, request: Request, db: Session = Depends(get_db)):
    # ❌ Authorization yoxlaması yoxdur!
    if not repo.delete(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted"}
```

**✅ Line 104-120:** `partial_update_product` - DÜZGÜNDÜR
```python
@router.patch("/products/{product_id}", response_model=Product)
async def partial_update_product(product_id: UUID, product_data: dict, request: Request, db: Session = Depends(get_db)):
    user_id = request.headers.get('x-user-id')  # ✅
    shop_id = await shop_client.get_shop_by_user_id(user_id)  # ✅
    
    # ✅ Authorization check var
    if not shop_id or str(existing_product.shop_id) != str(shop_id):
        raise HTTPException(status_code=403, detail="You can only update your own products")
```

---

## 💡 Həllər

### **1. ShopCart Service Fix**

**`routes.py`-də authorization yoxlaması əlavə edin:**

```python
from sqlalchemy.orm import Session
from fastapi import HTTPException

def verify_cart_ownership(db: Session, cart_id: int, user_uuid: str):
    """Yoxla ki bu cart bu user-a aiddir"""
    cart = db.query(models.ShopCart).filter(
        models.ShopCart.id == cart_id,
        models.ShopCart.user_uuid == user_uuid
    ).first()
    
    if not cart:
        raise HTTPException(
            status_code=403, 
            detail="You don't have access to this cart"
        )
    return cart


@router.post("/{cart_id}/items/{product_var_id}", response_model=schemas.CartItemRead)
async def add_item(
    cart_id: int,
    product_var_id: str, 
    item: schemas.CartItemCreate, 
    user_uuid: str = Depends(get_user_id),  # ✅ User ID alır
    db: Session = Depends(db.get_db)
):
    # ✅ Cart ownership yoxla
    verify_cart_ownership(db, cart_id, user_uuid)
    
    product_data = await product_client.get_product_data_by_variation_id(product_var_id)
    if not product_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_var_id} not found"
        )
    return crud.add_item_to_cart(db, product_var_id, cart_id, item)


@router.put("/{cart_id}/items/{item_id}", response_model=schemas.CartItemRead)
def update_cart_item(
    cart_id: int, 
    item_id: int, 
    item: schemas.CartItemUpdate, 
    user_uuid: str = Depends(get_user_id),  # ✅ User ID alır
    db: Session = Depends(db.get_db)
):
    # ✅ Cart ownership yoxla
    verify_cart_ownership(db, cart_id, user_uuid)
    
    updated_item = crud.update_cart(db, item_id, cart_id, item)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return updated_item


@router.delete("/{cart_id}/items/{item_id}", response_model=schemas.CartItemRead)
def delete_cart_item(
    cart_id: int, 
    item_id: int, 
    user_uuid: str = Depends(get_user_id),  # ✅ User ID alır
    db: Session = Depends(db.get_db)
):
    # ✅ Cart ownership yoxla
    verify_cart_ownership(db, cart_id, user_uuid)
    
    deleted_item = crud.delete_cart_item(db, item_id, cart_id)
    if not deleted_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return deleted_item
```

---

### **2. Product Service Fix**

**`routes.py`-də authorization əlavə edin:**

```python
@router.put("/products/{product_id}", response_model=Product)
async def update_product(
    product_id: UUID, 
    product: ProductCreate, 
    request: Request, 
    db: Session = Depends(get_db)
):
    user_id = request.headers.get('x-user-id')
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID required")
    
    # ✅ Product-u getir
    repo = ProductRepository(db)
    existing_product = repo.get(product_id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # ✅ Authorization check
    shop_id = await shop_client.get_shop_by_user_id(user_id)
    if not shop_id or str(existing_product.shop_id) != str(shop_id):
        raise HTTPException(status_code=403, detail="You can only update your own products")
    
    updated_product = repo.update(product_id, product)
    return updated_product


@router.delete("/products/{product_id}")
async def delete_product(
    product_id: UUID, 
    request: Request, 
    db: Session = Depends(get_db)
):
    user_id = request.headers.get('x-user-id')
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID required")
    
    # ✅ Product-u getir
    repo = ProductRepository(db)
    existing_product = repo.get(product_id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # ✅ Authorization check
    shop_id = await shop_client.get_shop_by_user_id(user_id)
    if not shop_id or str(existing_product.shop_id) != str(shop_id):
        raise HTTPException(status_code=403, detail="You can only delete your own products")
    
    if not repo.delete(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted"}
```

---

## 🎯 İndiki Vəziyyət vs Düzəldilmiş Vəziyyət

### **❌ İndiki Vəziyyət:**

```
1. Client → POST /shopcart/1/items/123
   Headers: { Authorization: Bearer token, X-User-Id: "user-b" }
   
2. Gateway → JWT verify edir ✅
   
3. Gateway → X-User-ID header ilə shopcart service-ə göndərir
   
4. ShopCart Service → Sadəcə cart_id=1 olduğuna görə əlavə edir ❌
   ❌ Cart user-b-a aididirmi yoxlamır!
```

### **✅ Düzəldilmiş Vəziyyət:**

```
1. Client → POST /shopcart/1/items/123
   Headers: { Authorization: Bearer token, X-User-Id: "user-b" }
   
2. Gateway → JWT verify edir ✅
   
3. Gateway → X-User-ID header ilə shopcart service-ə göndərir
   
4. ShopCart Service → 
   ✅ verify_cart_ownership(db, cart_id=1, user_uuid="user-b")
   ✅ Query: SELECT * FROM cart WHERE id=1 AND user_uuid='user-b'
   ✅ Əgər tapılmasa → 403 Forbidden
   ✅ Əgər tapsa → əməliyyat icra olunur
```

---

## 📊 Authorization Checklist

Hər endpoint üçün yoxlanmalıdır:

- [ ] **Authentication:** User token validdir? (Gateway edir)
- [ ] **Authorization:** User bu resource-a çatmaq hüququna malikdir?
  - [ ] Cart user-a aiddir? (ShopCart Service)
  - [ ] Product shop-a aiddir? (Product Service)
  - [ ] Order user-a aiddir? (Order Service)
  - [ ] Shop user-a aiddir? (Shop Service)

---

## 🎓 Xülasə

**Gateway yalnız Authentication edir:**
- Token validdir?
- User login olub?

**Backend servislər Authorization etməlidir:**
- User bu əməliyyatı edə bilərmi?
- User bu resource-a sahibidirmi?

**Yoxlanışlar:**
- ShopCart Service → Cart ownership check yoxdur ❌
- Product Service → Delete/Update-də ownership check yoxdur ❌
- Middleware yalnız token verify edir, ownership yoxlamır ❌

