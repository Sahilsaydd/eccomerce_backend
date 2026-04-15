from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from app.modules.cart.model.cart_model import Cart
from app.modules.cart.model.cart_item_model import CartItem
from app.modules.product.model.product_model import Product


# ✅ Get or create cart
async def get_or_create_cart(db, user_id):
    result = await db.execute(select(Cart).where(Cart.user_id == user_id))
    cart = result.scalars().first()

    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)

    return cart


# ✅ Add to cart
async def add_to_cart(db, user_id, data):
    cart = await get_or_create_cart(db, user_id)

    # check product exists
    result = await db.execute(select(Product).where(Product.id == data.product_id))
    product = result.scalars().first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # check item exists
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

    return {"message": "Item added to cart"}


# ✅ Get cart with product details
async def get_cart(db, user_id):
    cart = await get_or_create_cart(db, user_id)

    result = await db.execute(
        select(CartItem)
        .options(selectinload(CartItem.product))  # 🔥 IMPORTANT
        .where(CartItem.cart_id == cart.id)
    )

    items = result.scalars().all()

    # format response
    total_price = 0
    response = []

    for item in items:
        item_total = item.quantity * item.product.price
        total_price +=item_total
        response.append({
            "id": item.id,
            "quantity": item.quantity,
            "product": {
                "id": item.product.id,
                "name": item.product.name,
                "price": item.product.price,
                "category": item.product.category,
                "Item_total":"{:.2f}".format(item_total)

            },
        })
    response.append({
        "Total_price": "{:.2f}".format(total_price)
    })

    return response


# ✅ Remove item
async def remove_item(db, user_id, product_id):
    cart = await get_or_create_cart(db, user_id)

    result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        )
    )
    item = result.scalars().first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    await db.delete(item)
    await db.commit()

    return {"message": "Item removed"}


# ✅ Clear cart
async def clear_cart(db, user_id):
    cart = await get_or_create_cart(db, user_id)

    await db.execute(
        CartItem.__table__.delete().where(CartItem.cart_id == cart.id)
    )
    await db.commit()

    return {"message": "Cart cleared"}