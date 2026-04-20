import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, update ,func
from fastapi import HTTPException
from app.modules.product.model.product_model import Product

# Create Products

async def create_product(db:AsyncSession ,data):
    new_product = Product(**data.model_dump())
    print(f"New Product {new_product}")
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)
    return new_product

async def get_products(db: AsyncSession, redis):
    cache_key = "products:all"

    # 1. check cache sorted record in ascending order by id
    cached_data = await redis.get(cache_key)
     

    if cached_data:
        print("⚡ From Cache")
        return json.loads(cached_data)

    # 2. DB fallback
    print("🐢 From DB")
    result = await db.execute(
        select(Product).where(Product.is_active == True)
    )
    products = result.scalars().all()

    data = [

        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "description": p.description,
            "category": p.category
        }
        for p in products
    ]

    data.sort(key=lambda x: x["id"])
    # 3. store in redis
    await redis.set(
        cache_key,
        json.dumps(data),
        ex=120  # increase from 5 → 60
    )

    return data



# Implement pagination instead of the skip use the page and count of the total products and the count of the products per page
async def get_products_paginated(db:AsyncSession ,page:int =1 , per_page:int=10):
    total_products = await db.execute(select(func.count()).select_from(Product).where(Product.is_active == True))
    total_count = total_products.scalar()
    total_pages = (total_count + per_page - 1) // per_page

    if page < 1 or page > total_pages:
        raise HTTPException(status_code=400, detail="The page is not exsit")

    offset = (page - 1) * per_page
    result = await db.execute(select(Product).where(Product.is_active == True).order_by(Product.id).offset(offset).limit(per_page))
    products = result.scalars().all()

    return {
    "total_count": total_count,
    "total_pages": total_pages,
    "current_page": page,
    "products": products
}

#Get By id
async def get_product_by_id(db:AsyncSession,product_id:int):
    result = await db.execute(select(Product).where(Product.id==product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404 ,detail="Product Not Found")
    return product


#update product

async def update_product(db:AsyncSession, product_id:int, data):
    product = await get_product_by_id(db, product_id)

    for key ,value in data.model_dump(exclude_unset=True).items():
        setattr(product,key,value)

    await db.commit()
    await  db.refresh(product)
    return product


# delete product

async def delete_product(db: AsyncSession, product_id: int):
    product = await get_product_by_id(db, product_id)

    product.is_active = False   # 

    await db.commit()
    await db.refresh(product)

    return {"message": "Product deleted successfully (soft delete)" , "IsActive":product.is_active}


# search products
async def search_products(db:AsyncSession, keyword:str = None, category:str = None):
    query = select(Product)

    if keyword:
        query = query.where(Product.name.ilike(f"%{keyword}%"))
    if category:
        query = query.where(Product.category.ilike(f"%{category}%"))

    result = await db.execute(query)
    return result.scalars().all()


# delete all products
async def delete_all_products(db:AsyncSession):
    await db.execute(update(Product).values(is_active=False)) #  soft delete all)
    await db.commit()
    return {"message": "All products deleted successfully"}
  


#search

async def search_products(db:AsyncSession, keyword=None , category=None):
    query = select(Product)

    if(keyword):
        query = query.where(Product.name.ilike(f"%{keyword}%"))
    if(category):
        query =query.where(Product.category==category)
    
    result = await db.execute(query)
    return result.scalars().all()


# ## Delete All Products (For Testing Only)
# async def delete_all_products(db:AsyncSession):
#     await db.execute(text("DELETE FROM products"))
#     await db.commit()
#     return {"message":"All Products Deleted Successfully"}