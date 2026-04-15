from fastapi import APIRouter,Depends
from sqlalchemy.ext.asyncio  import AsyncSession
from app.deps.db import get_db
from app.deps.auth import get_current_user
from app.modules.cart.schemas.cart_schema import AddToCart
from app.modules.cart.crud import cart_crud

router =APIRouter(prefix="/cart", tags=["Cart"])

@router.post("/add")
async def add_to_cart(data:AddToCart, db:AsyncSession = Depends(get_db), user= Depends(get_current_user)):
    return await cart_crud.add_to_cart(db, user["user_id"] ,data)

@router.get("/")
async def get_cart(db:AsyncSession = Depends(get_db),user =Depends(get_current_user)):
     return await cart_crud.get_cart(db, user["sub"])

# remove item
@router.delete("/remove/{product_id}")
async def remove_item(product_id:int , db:AsyncSession=Depends(get_db), user=Depends(get_current_user)):
     return await cart_crud.remove_item(db, user["user_id"],product_id)


# Clear cart
@router.delete("/clear")
async def remove_data(db:AsyncSession =Depends(get_db) ,user =Depends(get_current_user)):
     return await cart_crud.clear_cart(db,user["sub"])
     