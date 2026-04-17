from sqlalchemy.future import select
from fastapi import HTTPException
from app.modules.order.model.order_model import Order
from app.modules.order.model.order_items_model import OrderItems
from app.modules.cart.model.cart_model import Cart
from app.modules.cart.model.cart_item_model import CartItem
from app.modules.product.model.product_model import Product
from app.modules.user.model.user import User

#  Import email functions
from app.utils.email import send_order_email, send_status_email


#  Create Order (Single Product Checkout)
async def create_order(db, user_id, product_id):

    #  Get user (for email)
    result = await db.execute(select(User).where(User.id == user_id, User.is_active==True))
    user = result.scalars().first()

    #  Get Cart
    result = await db.execute(select(Cart).where(Cart.user_id == user_id ,Cart.is_active == True))
    cart = result.scalars().first()

    if not cart:
        raise HTTPException(status_code=404, detail="Cart Not Found")

    #  Get specific product from cart
    result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id,
            CartItem.is_active == True
        )
    )
    cart_item = result.scalars().first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Product Not In Cart")

    #  Get product details
    result = await db.execute(select(Product).where(Product.id == product_id ,Product.is_active ==True))
    product = result.scalars().first()

    if not product:
        raise HTTPException(status_code=404, detail="Product Not Found")

    #  Create Order
    order = Order(user_id=user_id)
    db.add(order)
    await db.commit()
    await db.refresh(order)

    #  Create Order Item
    order_item = OrderItems(
        order_id=order.id,
        product_id=product_id,
        quantity=cart_item.quantity,
        price=product.price
    )

    db.add(order_item)

    #  Remove item from cart
    cart_item.is_active = False
    #await db.delete(cart_item)
    await db.commit()

    #   SEND EMAIL (Order Placed)
    if user:
        await send_order_email(user, order)

    return {
        "message": "Single Product Ordered Successfully",
        "order_id": order.id,
        "product_id": product_id,
        "Order Status": order.status,
        "Created At": order.created_at
    }


#  Get User Orders
async def get_orders(db, user_id):
    result = await db.execute(select(Order).where(Order.user_id == user_id,Order.is_active==True))
    orders = result.scalars().all()

    return [
        {
            "order_id": order.id,
            "status": order.status,
            "created_at": order.created_at,
            "Is Active":order.is_active
        }
        for order in orders
    ]


#  Get Order Details
async def get_order_details(db, order_id, user_id):

    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == user_id,
            Order.is_active == True
        )
    )
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order Not found")

    result = await db.execute(
        select(OrderItems).where(OrderItems.order_id == order.id ,OrderItems.is_active==True)
    )
    items = result.scalars().all()

    formatted_items = []

    for item in items:
        result = await db.execute(
            select(Product).where(Product.id == item.product_id ,OrderItems.is_active==True)
        )
        product = result.scalars().first()

        formatted_items.append({
            "product_id": item.product_id,
            "product_name": product.name if product else None,
            "quantity": item.quantity,
            "price": item.price
        })

    return {
        "order_id": order.id,
        "status": order.status,
        "created_at": order.created_at,
        "items": formatted_items,
        "IsActive":order.is_active
    }


#  Update Order Status (ADMIN)
async def update_order_status(db, order_id, status):

    result = await db.execute(select(Order).where(Order.id == order_id ,Order.is_active==True))
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order Not Found")

    #  Get user for email
    result = await db.execute(select(User).where(User.id == order.user_id ,User.is_active==True))
    user = result.scalars().first()

    #  Update status
    order.status = status
    await db.commit()
    await db.refresh(order)

    #   SEND EMAIL (Status Update)
    if user:
        await send_status_email(user, order)

    return {
        "message": "Order Status Updated",
        "order_id": order.id,
        "status": order.status,
        "IsActive":order.is_active
    }