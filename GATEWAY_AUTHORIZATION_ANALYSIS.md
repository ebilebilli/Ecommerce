# Gateway-da Authorization - Mümkündürmü?

## ❌ Qısa Cavab: **Texniki mümkündür, amma məsləhət DEYİL**

---

## 🔍 İndiki Vəziyyət

### ✅ **Gateway** (auth.py, middleware.py)
```python
# Authentication edir
- JWT token verify
- User ID extract
- X-User-ID header göndərir

# ❌ Authorization ETMİR
```

### ✅ **Backend Servis** (routes.py)
```python
# Authorization edir
def verify_cart_ownership(db, cart_id, user_uuid):
    cart = db.query(models.ShopCart).filter(
        models.ShopCart.id == cart_id,
        models.ShopCart.user_uuid == user_uuid
    ).first()
    if not cart:
        raise HTTPException(403, "You don't have access")
```

---

## 🚀 Gateway-da Authorization Etmək (Mümkündü amma...)

### **Nümunə İmplementasiya:**

```python
# gateway/auth.py
async def verify_cart_ownership(request: Request, cart_id: int):
    user_uuid = request.state.user.get('sub')
    
    # ❌ Database connection lazımdır
    async with httpx.AsyncClient() as client:
        # ❌ ShopCart Service-ə sorğu göndərir
        res = await client.get(f'{SERVICE_URLS["cart"]}/shopcart/ownership/{cart_id}', 
                              headers={"X-User-Id": user_uuid})
        
        if res.status_code != 200:
            raise HTTPException(403, "Cart ownership verification failed")
    
    return True


async def auth_middleware(request: Request, call_next):
    # 1. Authentication
    if path == '/user/api/user/login/':
        return await handle_login(request)
    
    # 2. Authorization (ƏƏVƏZ EDİLİR)
    path = request.url.path
    
    # Cart əməliyyatları üçün
    if '/shopcart' in path and '{cart_id}' in path:
        import re
        match = re.search(r'/shopcart/(\d+)/')
        if match:
            cart_id = int(match.group(1))
            # ❌ Hər request-də əlavə sorğu!
            await verify_cart_ownership(request, cart_id)
    
    # Product əməliyyatları üçün
    if '/products' in path and (request.method in ['PUT', 'DELETE']):
        # ❌ Hər dəfə product-u getir və ownership yoxla!
        pass
    
    response = await call_next(request)
    return response
```

---

## 📊 Problemlər

### **1. Performance Problemi**

```
Request Flow:

1. Client → Gateway
2. Gateway → Database sorğu (Cart ownership yoxla)
3. Gateway → ShopCart service sorğusu
4. ShopCart service → Database sorğu (əslində eyni şey!)
5. Response qaytar

❌ İKİ DƏFƏ DATABASE SORĞUSU!
```

### **2. Complexity Problemi**

Gateway-da hər endpoint üçün business logic:

```python
# gateway/auth.py - ARTİQ ÇOX BOYÜDÜR!

async def verify_cart_ownership(request, cart_id): ...
async def verify_product_ownership(request, product_id): ...
async def verify_order_ownership(request, order_id): ...
async def verify_shop_ownership(request, shop_id): ...
async def verify_shop_admin(request, shop_id): ...
async def verify_comment_ownership(request, comment_id): ...

# Həm də bu sayıda endpoint lazımdır!
```

### **3. Database Coupling**

```python
# Gateway-ə lazımdır:
from sqlalchemy import create_engine
from shopcart_service.models import ShopCart
from product_service.models import Product
from shop_service.models import Shop
# ... və s

# Gateway.hər service-in database-inə bağlanmalıdır!
```

### **4. Service-Specific Logic**

Hər service-in öz business logic-i var:

```python
# ShopCart-də:
# - Cart boş deyil
# - Item limit var
# - Free delivery threshold var

# Product-də:
# - Product silinə bilər (anınkı order yoxdursa)
# - Variation merge oluna bilər
# - Image priority var

# Gateway-da bütün bunları bilmək lazımdır! ❌
```

---

## ✅ Best Practice: Niyə Backend-də?

### **Separation of Concerns**

```
Gateway (API Gateway):
├─ Authentication ✅
│  └─ Token verify, user extract
└─ Request Forwarding ✅

Backend Service:
├─ Business Logic ✅
├─ Authorization ✅
│  └─ Ownership checks
└─ Data Validation ✅
```

### **Microservice Architecture**

```
Gateway (Thin Layer):
- Şərhsiz request forwarding
- Minimal business logic

Backend Services (Fat Logic):
- Business rules
- Data validation  
- Authorization
- Domain logic
```

---

## 💡 Mümkün Kompromis: Gateway + Backend Hybrid

### **1. Yalnız Sadə Authorization**

Gateway yalnız **əlamətli (flag-based)** yoxlamalar edə bilər:

```python
# gateway/auth.py
PUBLIC_PATHS = [...]  # ✅ Sadə

# Backend-də ağır yoxlamalar:
def verify_cart_ownership(...)  # ✅ Detailed
```

### **2. Gateway-da Pre-Checks**

Gateway sadə yoxlamalar edir, ağırları backend-də qalır:

```python
# Gateway: Sadə
if not user_id:
    return 401

# Backend: Detallı
def verify_cart_ownership(db, cart_id, user_uuid):
    cart = db.query(...).filter(...).first()
    if not cart or cart.user_uuid != user_uuid:
        raise 403
    if cart.status == 'LOCKED':
        raise 423
    # ... və s
```

---

## 🎯 Tövsiyə

### **İndiki Architektura (✅ Düzgündür)**

```
┌──────────┐
│ Gateway  │ → Authentication (token verify)
└────┬─────┘
     │
     ├───> ShopCart Service → Authorization (cart ownership)
     ├───> Product Service → Authorization (product ownership)
     └───> Order Service  → Authorization (order ownership)
```

**Üstünlüklər:**
- ✅ Gateway sadə və sürətli qalır
- ✅ Backend services öz business logic-ni bilir
- ✅ Dəyişikliklər asandır
- ✅ Service isolation

**Mənfilikləri:**
- ❌ Hər service-də authorization kodu lazımdır
- ❌ Çox yerdə kod tekrarı olur

---

## 📝 Xülasə

**Sual:** Gateway-da authorization etmək olar?

**Cavab:** 
- ✅ Texniki mümkündür
- ❌ Amma məsləhət deyil
- ✅ İndiki yol (Gateway=Auth, Backend=Authorization) daha yaxşıdır

**Əsas səbəb:**
Gateway çox mürəkkəb olacaq, database coupling problemləri yaranacaq, microservice prinsip pozulacaq.

**Yerinə:**
- Gateway-da sadə authentication
- Backend-də detallı authorization

