from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, BackgroundTasks

from app.deps import db
from app.modules.cart.model.cart_model import Cart
from app.modules.cart.model.cart_item_model import CartItem
from app.modules.product.model.product_model import Product
from app.modules.user.model.user import User

from app.utils.email import send_cart_email


async def get_or_create_cart(db, user_id):
    result = await db.execute(select(Cart).where(Cart.user_id == user_id))
    cart = result.scalars().first()

    if  cart and not cart.is_active:
        cart.is_active = True
        #cart = Cart(user_id=user_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
        return cart
    if not cart:
        cart = Cart(user_id=user_id, is_active=True)
        db.add(cart)
        await db.commit() 
        await db.refresh(cart)
        return cart
    return cart

    



async def add_to_cart(db, user_id, data, background_tasks: BackgroundTasks):
    cart = await get_or_create_cart(db, user_id)

    result = await db.execute(
        select(Product).where(Product.id == data.product_id, Product.is_active == True)
    )
    product = result.scalars().first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == data.product_id,
            CartItem.is_active == True   # ✅ only active
        )
        )
    item = result.scalars().first()

    if item:
        item.quantity += data.quantity

        if item.quantity <= 0:
            item.is_active = False

        await db.commit()

        if item.is_active:
            await db.refresh(item)

        return {"message": "Cart updated"}

    if data.quantity > 0:
        new_item = CartItem(
            cart_id=cart.id,
            product_id=data.product_id,
            quantity=data.quantity,
            is_active=True
        )
        db.add(new_item)
        await db.commit()
        await db.refresh(new_item)

        return {"message": "Item added to cart"}

    return {"message": "No item to update"}


async def get_cart(db, user_id):
    cart = await get_or_create_cart(db, user_id)

    result = await db.execute(
        select(CartItem)
        .options(selectinload(CartItem.product))
        .where(
            CartItem.cart_id == cart.id,
            CartItem.is_active == True   # ✅ only active cart items
        )
    )

    items = result.scalars().all()

    total_price = 0
    response_items = []

    for item in items:

        # ✅ IMPORTANT: Skip inactive products
        if not item.product or item.product.is_active == False:
            continue

        # Calculate Discounted Price
        discounted_price = item.product.price
        if item.product.discount_percentage > 0:
            discounted_price = item.product.price * (1 - item.product.discount_percentage / 100)

        item_total = item.quantity * discounted_price
        total_price += item_total

        response_items.append({
            "id": item.id,
            "quantity": item.quantity,
            "product": {
                "id": item.product.id,
                "name": item.product.name,
                "price": item.product.price,
                "discount_price": round(discounted_price, 2),
                "discount_percentage": item.product.discount_percentage,
                "category": item.product.category,
                "image": item.product.product_img,
                "description": item.product.description,
            },
        })

    return {
        "items": response_items,
        "total_price": round(total_price, 2)
    }

async def remove_item(db, user_id, product_id, background_tasks: BackgroundTasks):
    cart = await get_or_create_cart(db, user_id)

    result = await db.execute(
        select(CartItem)
        .where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id,
            CartItem.is_active == True   # ✅ only active item
        )
    )
    item = result.scalars().first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.is_active = False
    await db.commit()

    return {"message": "Item removed from cart"}

async def clear_cart(db, user_id, background_tasks: BackgroundTasks):
    cart = await get_or_create_cart(db, user_id)

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    await db.execute(
       update(CartItem).where(CartItem.cart_id ==cart.id).values(is_active =False)
    )
    await db.commit()

    if user:
        background_tasks.add_task(
            send_cart_email,
            user,
        )

    return {"message": "Cart cleared successfully"}