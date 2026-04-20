from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.db import get_db
from app.deps.auth import get_current_user
from app.modules.cart.schemas.cart_schema import AddToCart
from app.modules.cart.crud import cart_crud

router = APIRouter(prefix="/cart", tags=["Cart"])


#  Add to cart
@router.post("/add")
async def add_to_cart(
    background_tasks: BackgroundTasks,
    data: AddToCart,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    user_id = int(user["sub"])  #  Convert sub (user.id) to int
    return await cart_crud.add_to_cart(db, user_id, data , background_tasks)


#  Get cart
@router.get("/")
async def get_cart(
    
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    user_id = int(user["sub"])  #  Convert sub (user.id) to int
    return await cart_crud.get_cart(db, user_id)


#  Remove item
@router.delete("/remove/{product_id}")
async def remove_item(
    background_tasks: BackgroundTasks,
    product_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    user_id = int(user["sub"])  #  Convert sub (user.id) to int
    return await cart_crud.remove_item(db, user_id, product_id, background_tasks)


#  Clear cart
@router.delete("/clear")
async def clear_cart(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    user_id = int(user["sub"])  #  Convert sub (user.id) to int
    return await cart_crud.clear_cart(db, user_id, background_tasks)