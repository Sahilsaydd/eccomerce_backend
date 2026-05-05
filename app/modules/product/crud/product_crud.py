import json

from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.product.model.product_model import Product


def calculate_final_price(price: float, discount: int):
    if not discount:
        return price
    return round(price - (price * discount / 100), 2)


def format_product_response(product: Product):
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
        "product_images": product.product_images or [],
    }


async def create_product(db: AsyncSession, data, redis=None):
    if hasattr(data, "model_dump"):
        data = data.model_dump()

    new_product = Product(**data)

    db.add(new_product)
    await db.commit()
    await db.refresh(new_product)

    if redis:
        await redis.delete("products:all:v2")

    return format_product_response(new_product)


async def get_products(db: AsyncSession, redis):
    cache_key = "products:all:v2"

    cached_data = await redis.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    result = await db.execute(select(Product).where(Product.is_active == True))
    products = result.scalars().all()

    data = [format_product_response(product) for product in products]
    data.sort(key=lambda item: item["id"])

    await redis.set(cache_key, json.dumps(data), ex=60)
    return data


async def get_products_paginated(db: AsyncSession, page: int = 1, per_page: int = 10):
    total_products = await db.execute(
        select(func.count()).select_from(Product).where(Product.is_active == True)
    )
    total_count = total_products.scalar()
    total_pages = (total_count + per_page - 1) // per_page

    if total_count == 0:
        return {
            "total_count": 0,
            "total_pages": 0,
            "current_page": page,
            "products": [],
        }

    if page < 1 or page > total_pages:
        raise HTTPException(status_code=400, detail="Page does not exist")

    offset = (page - 1) * per_page
    result = await db.execute(
        select(Product)
        .where(Product.is_active == True)
        .order_by(Product.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    products = result.scalars().all()

    return {
        "total_count": total_count,
        "total_pages": total_pages,
        "current_page": page,
        "products": [format_product_response(product) for product in products],
    }


async def get_product_by_id(db: AsyncSession, product_id: int):
    product = await get_product_by_id_raw(db, product_id)
    return format_product_response(product)


async def search_products(db: AsyncSession, keyword: str = None, category: str = None):
    query = select(Product).where(Product.is_active == True)

    if keyword:
        query = query.where(Product.name.ilike(f"%{keyword}%"))

    if category:
        query = query.where(Product.category.ilike(f"%{category}%"))

    result = await db.execute(query)
    products = result.scalars().all()
    return [format_product_response(product) for product in products]


async def update_product(db: AsyncSession, product_id: int, data, redis=None):
    product = await get_product_by_id_raw(db, product_id)

    if hasattr(data, "model_dump"):
        update_data = data.model_dump(exclude_unset=True)
    else:
        update_data = {key: value for key, value in data.items() if value is not None}

    for key, value in update_data.items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)

    if redis:
        await redis.delete("products:all:v2")

    return format_product_response(product)


async def delete_product(db: AsyncSession, product_id: int, redis):
    product = await get_product_by_id_raw(db, product_id)
    product.is_active = False

    await db.commit()
    await db.refresh(product)
    await redis.delete("products:all:v2")

    return {
        "Product_id": product.id,
        "message": "Product deleted successfully",
        "is_active": product.is_active,
    }


async def delete_all_products(db: AsyncSession, redis=None):
    await db.execute(update(Product).values(is_active=False))
    await db.commit()

    if redis:
        await redis.delete("products:all:v2")

    return {"message": "All products deleted successfully"}


async def get_product_by_id_raw(db: AsyncSession, product_id: int):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product Not Found")

    return product
