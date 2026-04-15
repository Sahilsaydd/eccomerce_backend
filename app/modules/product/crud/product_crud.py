from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
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


## Get All Products
async def get_products(db:AsyncSession):
    result = await db.execute(select(Product))
    return  result.scalars().all()


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

async def delete_product(db:AsyncSession ,product_id:int):
    product = await get_product_by_id(db,product_id)

    await db.delete(product)
    await db.commit()
    return {"message": "Product deleted successfully"}


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
    await db.execute(text("DELETE FROM products"))
    await db.commit()
    return {"message": "All products deleted successfully"}
    await db.commit()
    return {"massage":"Product Deleted Successfully"}


#search

async def search_products(db:AsyncSession, keyword=None , category=None):
    query = select(Product)

    if(keyword):
        query = query.where(Product.name.ilike(f"%{keyword}%"))
    if(category):
        query =query.where(Product.category==category)
    
    result = await db.execute(query)
    return result.scalars().all()


## Delete All Products (For Testing Only)
async def delete_all_products(db:AsyncSession):
    await db.execute(text("DELETE FROM products"))
    await db.commit()
    return {"message":"All Products Deleted Successfully"}