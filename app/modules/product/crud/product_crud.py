import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from fastapi import HTTPException
from app.modules.product.model.product_model import Product




def calculate_final_price(price: float, discount: int):
    if not discount:
        return price
    return round(price - (price * discount / 100), 2)




async def create_product(db: AsyncSession, data):
    new_product = Product(**data.model_dump())
    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)

    final_price = calculate_final_price(new_product.price, new_product.discount_percentage)

    return {
        "id": new_product.id,
        "name": new_product.name,
        "price": new_product.price,
        "final_price": final_price,
        "you_saved": round(new_product.price - final_price, 2),
        "description": new_product.description,
        "category": new_product.category,
        "rating": new_product.rating,
        "product_img": new_product.product_img,
        "stock": new_product.stock,
        "brand": new_product.brand,
        "discount_percentage": new_product.discount_percentage,
        "product_images": new_product.product_images
    }




async def get_products(db: AsyncSession, redis):
    cache_key = "products:all:v2"

    cached_data = await redis.get(cache_key)
    if cached_data:
        print("⚡ From Cache")
        return json.loads(cached_data)

    print("🐢 From DB")
    result = await db.execute(
        select(Product).where(Product.is_active == True)
    )
    products = result.scalars().all()

    data = []
    for p in products:
        final_price = calculate_final_price(p.price, p.discount_percentage)

        data.append({
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "final_price": final_price,
            "you_saved": round(p.price - final_price, 2),
            "description": p.description,
            "category": p.category,
            "rating": p.rating,
            "product_img": p.product_img,
            "stock": p.stock,
            "brand": p.brand,
            "discount_percentage": p.discount_percentage,
            "product_images": p.product_images
        })

    data.sort(key=lambda x: x["id"])

    await redis.set(cache_key, json.dumps(data), ex=60)

    return data



async def get_products_paginated(db: AsyncSession, page: int = 1, per_page: int = 10):

    total_products = await db.execute(
        select(func.count()).select_from(Product).where(Product.is_active == True)
    )
    total_count = total_products.scalar()
    total_pages = (total_count + per_page - 1) // per_page

    if page < 1 or page > total_pages:
        raise HTTPException(status_code=400, detail="Page does not exist")

    offset = (page - 1) * per_page

    result = await db.execute(
        select(Product)
        .where(Product.is_active == True)
        .order_by(Product.id)
        .offset(offset)
        .limit(per_page)
    )

    products = result.scalars().all()

    formatted_products = []
    for p in products:
        final_price = calculate_final_price(p.price, p.discount_percentage)

        formatted_products.append({
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "final_price": final_price,
            "you_saved": round(p.price - final_price, 2),
            "description": p.description,
            "category": p.category,
            "rating": p.rating,
            "product_img": p.product_img,
            "stock": p.stock,
            "brand": p.brand,
            "discount_percentage": p.discount_percentage,
            "product_images": p.product_images
        })

    return {
        "total_count": total_count,
        "total_pages": total_pages,
        "current_page": page,
        "products": formatted_products
    }



async def get_product_by_id(db: AsyncSession, product_id: int):
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    p = result.scalar_one_or_none()

    if not p:
        raise HTTPException(status_code=404, detail="Product Not Found")

    final_price = calculate_final_price(p.price, p.discount_percentage)

    return {
        "id": p.id,
        "name": p.name,
        "price": p.price,
        "final_price": final_price,
        "you_saved": round(p.price - final_price, 2),
        "description": p.description,
        "category": p.category,
        "rating": p.rating,
        "product_img": p.product_img,
        "stock": p.stock,
        "brand": p.brand,
        "discount_percentage": p.discount_percentage,
        "product_images": p.product_images
    }



async def search_products(db: AsyncSession, keyword: str = None, category: str = None):
    query = select(Product).where(Product.is_active == True)

    if keyword:
        query = query.where(Product.name.ilike(f"%{keyword}%"))

    if category:
        query = query.where(Product.category.ilike(f"%{category}%"))

    result = await db.execute(query)
    products = result.scalars().all()

    data = []
    for p in products:
        final_price = calculate_final_price(p.price, p.discount_percentage)

        data.append({
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "final_price": final_price,
            "you_saved": round(p.price - final_price, 2),
            "description": p.description,
            "category": p.category,
            "rating": p.rating,
            "product_img": p.product_img,
            "stock": p.stock,
            "brand": p.brand,
            "discount_percentage": p.discount_percentage,
            "product_images": p.product_images
        })

    return data






async def update_product(db: AsyncSession, product_id: int, data):
    product = await get_product_by_id_raw(db, product_id)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)

    final_price = calculate_final_price(product.price, product.discount_percentage)

    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "final_price": final_price,
        "you_saved": round(product.price - final_price, 2),
        "description": product.description,
        "category": product.category,
        "rating": product.rating,
        "product_img": product.product_img,
        "stock": product.stock,
        "brand": product.brand,
        "discount_percentage": product.discount_percentage,
        "product_images": product.product_images
    }




async def delete_product(db: AsyncSession, product_id: int, redis):
    product = await get_product_by_id_raw(db, product_id)

    product.is_active = False

    await db.commit()
    await db.refresh(product)
      # ✅ REMOVE CACHE (CRITICAL FIX)
    await redis.delete("products:all:v2")
    return {
         "Product_id": product.id,
        "message": "Product deleted successfully",
        "is_active": product.is_active
    }





async def delete_all_products(db: AsyncSession):
    await db.execute(update(Product).values(is_active=False))
    await db.commit()

    return {"message": "All products deleted successfully"}




async def get_product_by_id_raw(db: AsyncSession, product_id: int):
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product Not Found")

    return product