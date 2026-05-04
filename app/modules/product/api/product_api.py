import os
import shutil
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import require_role
from app.deps.db import get_db
from app.deps.redis import get_redis
from app.modules.product.crud import product_crud
from app.modules.product.schemas.product_schema import (
    PaginatedProductResponse,
    ProductResponse,
)

UPLOAD_DIR = "uploads/products"

router = APIRouter(prefix="/products", tags=["Products"])


def save_uploaded_file(upload_file: UploadFile) -> str:
    filename = f"{uuid4()}_{upload_file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return f"/uploads/products/{filename}"


@router.get("/paginated", response_model=PaginatedProductResponse)
async def get_paginated(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),
    db: AsyncSession = Depends(get_db),
):
    return await product_crud.get_products_paginated(db, page, per_page)


@router.get("/search/")
async def search(
    keyword: str = Query(None),
    category: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await product_crud.search_products(db, keyword, category)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_one(product_id: int, db: AsyncSession = Depends(get_db)):
    return await product_crud.get_product_by_id(db, product_id)


@router.get("/", response_model=list[ProductResponse])
async def get_all(db: AsyncSession = Depends(get_db), redis=Depends(get_redis)):
    return await product_crud.get_products(db, redis)


@router.post("/", response_model=ProductResponse)
async def create(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    stock: int = Form(0),
    brand: Optional[str] = Form(None),
    discount_percentage: int = Form(0),
    rating: float = Form(0),
    image: UploadFile = File(...),
    images: List[UploadFile] = File([]),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    user=Depends(require_role(["admin"])),
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    if not image:
        raise HTTPException(status_code=400, detail="Main image is required")

    image_path = save_uploaded_file(image)
    image_paths = [save_uploaded_file(img) for img in images]

    data = {
        "name": name,
        "description": description,
        "price": price,
        "category": category,
        "stock": stock,
        "brand": brand,
        "discount_percentage": discount_percentage,
        "rating": rating,
        "product_img": image_path,
        "product_images": image_paths,
    }

    return await product_crud.create_product(db, data, redis)


@router.put("/{product_id}", response_model=ProductResponse)
async def update(
    product_id: int,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    stock: int = Form(0),
    brand: Optional[str] = Form(None),
    discount_percentage: int = Form(0),
    rating: float = Form(0),
    image: UploadFile = File(None),
    images: List[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    user=Depends(require_role(["admin"])),
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    product = await product_crud.get_product_by_id_raw(db, product_id)

    image_path = product.product_img
    image_paths = product.product_images or []

    if image:
        image_path = save_uploaded_file(image)

    if images:
        image_paths = [save_uploaded_file(img) for img in images]

    data = {
        "name": name,
        "description": description,
        "price": price,
        "category": category,
        "stock": stock,
        "brand": brand,
        "discount_percentage": discount_percentage,
        "rating": rating,
        "product_img": image_path,
        "product_images": image_paths,
    }

    return await product_crud.update_product(db, product_id, data, redis)


@router.delete("/delete_all")
async def delete_all(
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    user=Depends(require_role(["admin"])),
):
    return await product_crud.delete_all_products(db, redis)


@router.delete("/{product_id}")
async def delete(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(["admin"])),
    redis=Depends(get_redis),
):
    return await product_crud.delete_product(db, product_id, redis)
