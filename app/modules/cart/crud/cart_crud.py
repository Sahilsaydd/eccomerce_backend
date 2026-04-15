from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy import text

from app.modules.cart.model.cart_model import Cart
from app.modules.cart.model.cart_item_model import CartItem
from app.modules.product.model.product_model import Product


# ✅ Get or create cart
async def get_or_create_cart(db: AsyncSession, user_id: int):
    result = await db.execute(select(Cart).where(Cart.user_id == user_id))
    cart = result.scalars().first()

    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)

    return cart


# ✅ Add to cart
async def add_to_cart(db: AsyncSession, user_id: int, data):
    
    # 🔥 Check product exists
    product_result = await db.execute(
        select(Product).where(Product.id == data.product_id)
    )
    product = product_result.scalars().first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    cart = await get_or_create_cart(db, user_id)

    result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == data.product_id
        )
    )
    item = result.scalars().first()

    if item:
        item.quantity += data.quantity
    else:
        item = CartItem(
            cart_id=cart.id,
            product_id=data.product_id,
            quantity=data.quantity
        )
        db.add(item)

    await db.commit()
    await db.refresh(item)

    return {"message": "Item added to cart successfully"}


# ✅ Get cart items
async def get_cart(db: AsyncSession, user_id: int):
    cart = await get_or_create_cart(db, user_id)

    result = await db.execute(
        select(CartItem).where(CartItem.cart_id == cart.id)
    )

    items = result.scalars().all()

    return items


# ✅ Remove item
async def remove_item(db: AsyncSession, user_id: int, product_id: int):
    cart = await get_or_create_cart(db, user_id)

    result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        )
    )
    item = result.scalars().first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item not found in cart"
        )

    await db.delete(item)
    await db.commit()

    return {"message": "Item removed successfully"}


# ✅ Clear cart
async def clear_cart(db: AsyncSession, user_id: int):
    cart = await get_or_create_cart(db, user_id)

    await db.execute(
        text("DELETE FROM cart_items WHERE cart_id = :cart_id"),
        {"cart_id": cart.id}
    )
    await db.commit()

    return {"message": "Cart cleared successfully"}