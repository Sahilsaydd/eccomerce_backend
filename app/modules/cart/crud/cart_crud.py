from sqlalchemy.future import select
from app.modules.cart.model.cart_model import Cart
from app.modules.cart.model.cart_item_model import CartItem
from app.modules.product.model.product_model import Product


#Get Or Create the cart
async def get_or_create_cart(db ,user_id):
    result = await db.execute(select(Cart).where(Cart.user_id == user_id))
    cart = result.scalars().first()
    if not cart:
        cart = Cart(user_id =user_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
    return cart



 # Add to cart
async def add_to_cart(db,user_id,data):
    cart = await get_or_create_cart(db,user_id)

    # Check if item already exists
    result = await db.execute(
        select(CartItem).where(
          CartItem.cart_id == cart.id,
          CartItem.product_id == data.product_id
        )
    )
    item = result.scalars().first()

    if item:
        # Update quantity
        item.quantity += data.quantity
    else:
        # Create new item
        item = CartItem(
            cart_id=cart.id,
            product_id=data.product_id,
            quantity=data.quantity
        )
        db.add(item)

    await db.commit()
    await db.refresh(item)
    return {"message": "Item added to cart successfully"}



async def get_cart(db,user_id):
     cart =await get_or_create_cart(db, user_id)

     result =await db.execute(select(CartItem).where(CartItem.cart_id==cart.id))
     return result.scalars().all()


#Remove Item
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
        return {"message": "Item not found in cart"}

    await db.delete(item)
    await db.commit()
    return {"message": "Item removed from cart successfully"}


# Clear cart
async def clear_cart(db, user_id):
    cart = await get_or_create_cart(db, user_id)

    await db.execute(text(f"DELETE FROM cart_items WHERE cart_id = {cart.id}"))
    await db.commit()
    return {"message": "Cart cleared successfully"}
async def  remove_item(db, user_id,product_id):
    cart = await get_or_create_db(db, user_id)
    result = db.execute(select(CartItem).where(CartItem.cart_id == cart.id ,CartItem.product_id == product_id))
    item = result.scalars().first()
    if item:
        await db.delete(item)
        await db.commit()
    return {"massage":"Item removed"}
         





## Clear Cart 

async def clear_cart(db, user_id):
    cart  = await get_or_create_db(db,user_id)
    await db.execute(
        CartItem.__table__.delete().where(CartItem.cart_id == Cart.id)

    )
    await db.commit()

    return {"massage":"Cart Cleared"}
