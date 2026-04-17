from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, BackgroundTasks

from app.modules.cart.model.cart_model import Cart
from app.modules.cart.model.cart_item_model import CartItem
from app.modules.product.model.product_model import Product
from app.modules.user.model.user import User

from app.utils.email import send_cart_email


#  Get or create cart
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

    



#  Add to cart (WITH EMAIL)
async def add_to_cart(db, user_id, data, background_tasks: BackgroundTasks):
    cart = await get_or_create_cart(db, user_id)

    # Get user (for email)
    result = await db.execute(select(User).where(User.id == user_id ))
    user = result.scalars().first()

    # Check product exists
    result = await db.execute(select(Product).where(Product.id == data.product_id ,Product.is_active == True))
    product = result.scalars().first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if item already exists
    result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == data.product_id,
            CartItem.is_active == True   # ✅
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

    #  Send email in background
    if user:
        background_tasks.add_task(send_cart_email, user, product)

    return {"message": "Item added to cart successfully","Product Name":product.name}


#  Get cart with product details
async def get_cart(db, user_id):
    cart = await get_or_create_cart(db, user_id)

    result = await db.execute(
        select(CartItem)
        .options(selectinload(CartItem.product))
        .where(CartItem.cart_id == cart.id ,CartItem.is_active == True)
    )

    items = result.scalars().all()

    total_price = 0
    response = []

    for item in items:
        item_total = item.quantity * item.product.price
        total_price += item_total

        response.append({
            "id": item.id,
            "quantity": item.quantity,
            "product": {
                "id": item.product.id,
                "name": item.product.name,
                "price": item.product.price,
                "category": item.product.category,
                "item_total": "{:.2f}".format(item_total)
            },
        })

    response.append({
        "total_price": "{:.2f}".format(total_price)
    })

    return response


#  Remove item (WITH EMAIL)
async def remove_item(db, user_id, product_id, background_tasks: BackgroundTasks):
    cart = await get_or_create_cart(db, user_id)

    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    result = await db.execute(
        select(CartItem)
        .options(selectinload(CartItem.product))
        .where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        )
    )
    item = result.scalars().first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    product = item.product

    item.is_active = False
    await db.commit()

    #  Optional: send email
    if user and product:
        background_tasks.add_task(
            send_cart_email,
            user,
            product
        )

    return {"message": "Item removed from cart" ,"Item":item}


#  Clear cart (WITH EMAIL)
async def clear_cart(db, user_id, background_tasks: BackgroundTasks):
    cart = await get_or_create_cart(db, user_id)

    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    await db.execute(
       update(CartItem).where(CartItem.cart_id ==cart.id).values(is_active =False)
    )
    await db.commit()

    #  Optional email
    if user:
        background_tasks.add_task(
            send_cart_email,
            user,
            type("Product", (), {"name": "All items"})()  # dummy object
        )

    return {"message": "Cart cleared successfully"}