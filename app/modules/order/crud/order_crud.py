from sqlalchemy.future import select
from fastapi import HTTPException
from app.modules.order.model.order_model import Order
from app.modules.order.model.order_items_model import OrderItems
from app.modules.cart.model.cart_model import Cart
from app.modules.cart.model.cart_item_model import CartItem
from app.modules.product.model.product_model import Product
from app.modules.user.model.user import User

from app.utils.email import send_order_email, send_status_email


async def create_order(db, user_id, product_id, data):

    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    user = result.scalars().first()

    result = await db.execute(
        select(Cart).where(Cart.user_id == user_id, Cart.is_active == True)
    )
    cart = result.scalars().first()

    if not cart:
        raise HTTPException(status_code=404, detail="Cart Not Found")

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

    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.is_active == True)
    )
    product = result.scalars().first()

    if not product:
        raise HTTPException(status_code=404, detail="Product Not Found")

    total_price = product.price * cart_item.quantity

    order = Order(
        user_id=user_id,
        total_price=total_price,
        name=data.name,
        phone=data.phone,
        address=data.address
    )

    db.add(order)
    await db.commit()
    await db.refresh(order)

    order_item = OrderItems(
        order_id=order.id,
        product_id=product_id,
        quantity=cart_item.quantity,
        price=product.price
    )

    db.add(order_item)

    cart_item.is_active = False

    await db.commit()

    if user:
        await send_order_email(user, order)

    return {
        "message": "Single Product Ordered Successfully",
        "order_id": order.id,
        "product_id": product_id,
        "status": order.status,
        "total_price": order.total_price,
        "created_at": order.created_at
    }


async def get_orders(db, user_id):

    result = await db.execute(
        select(Order).where(Order.user_id == user_id, Order.is_active == True)
        .order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()

    enriched = []
    for order in orders:
        # Get first order item to show product info
        items_result = await db.execute(
            select(OrderItems).where(
                OrderItems.order_id == order.id,
                OrderItems.is_active == True
            )
        )
        items = items_result.scalars().all()

        first_product_name = None
        first_quantity = None
        if items:
            prod_result = await db.execute(
                select(Product).where(Product.id == items[0].product_id)
            )
            product = prod_result.scalars().first()
            first_product_name = product.name if product else f"Product #{items[0].product_id}"
            first_quantity = items[0].quantity

        enriched.append({
            "order_id": order.id,
            "status": order.status,
            "total_price": float(order.total_price) if order.total_price else 0.0,
            "created_at": order.created_at,
            "name": order.name,
            "phone": order.phone,
            "address": order.address,
            "product_name": first_product_name,
            "quantity": first_quantity,
            "is_active": order.is_active
        })

    return enriched


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
        raise HTTPException(status_code=404, detail="Order Not Found")

    result = await db.execute(
        select(OrderItems).where(
            OrderItems.order_id == order.id,
            OrderItems.is_active == True
        )
    )
    items = result.scalars().all()

    formatted_items = []

    for item in items:
        result = await db.execute(
            select(Product).where(
                Product.id == item.product_id,
            )
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
        "total_price": order.total_price,
        "created_at": order.created_at,

        "name": order.name,
        "phone": order.phone,
        "address": order.address,

        "items": formatted_items,
        "is_active": order.is_active
    }


async def update_order_status(db, order_id, status):

    result = await db.execute(
        select(Order).where(Order.id == order_id, Order.is_active == True)
    )
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order Not Found")

    result = await db.execute(
        select(User).where(User.id == order.user_id, User.is_active == True)
    )
    user = result.scalars().first()

    order.status = status
    await db.commit()
    await db.refresh(order)

    if user:
        await send_status_email(user, order)

    return {
        "message": "Order Status Updated",
        "order_id": order.id,
        "status": order.status,
        "total_price": order.total_price,
        "is_active": order.is_active
    }