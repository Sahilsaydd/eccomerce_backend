from sqlalchemy.future import select
from sqlalchemy import func
from fastapi import HTTPException
from app.modules.order.model.order_model import Order
from app.modules.order.model.order_items_model import OrderItems
from app.modules.cart.model.cart_model import Cart
from app.modules.cart.model.cart_item_model import CartItem
from app.modules.product.model.product_model import Product
from app.modules.user.model.user import User
from sqlalchemy.orm import selectinload

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

    # Stock Management
    if product.stock < cart_item.quantity:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient stock. Only {product.stock} items left."
        )
    
    product.stock -= cart_item.quantity
    
    # Calculate Discounted Price for Order
    discounted_price = product.price
    if product.discount_percentage > 0:
        discounted_price = product.price * (1 - product.discount_percentage / 100)

    total_price = discounted_price * cart_item.quantity

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
    await db.refresh(product)

    order_item = OrderItems(
        order_id=order.id,
        product_id=product_id,
        quantity=cart_item.quantity,
        price=discounted_price
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



async def get_orders(db, user_id=None, is_admin=False):

    query = select(Order).where(Order.is_active == True)

    if not is_admin:
        query = query.where(Order.user_id == user_id)

    query = query.order_by(Order.created_at.desc())

    result = await db.execute(query)
    orders = result.scalars().all()

    enriched = []

    for order in orders:
        items_result = await db.execute(
            select(OrderItems).where(
                OrderItems.order_id == order.id,
                OrderItems.is_active == True
            )
        )
        items = items_result.scalars().all()

        item_list = []

        for item in items:
            prod_result = await db.execute(
                select(Product).where(Product.id == item.product_id)
            )
            product = prod_result.scalars().first()

            item_list.append({
                "quantity": item.quantity,
                "price": float(item.price),
                "product": {
                    "id": product.id if product else None,
                    "name": product.name if product else "Unknown",
                    "image": product.product_img if product else None,
                    "price": float(product.price) if product else 0
                }
            })

        enriched.append({
            "id": order.id,
            "user_id": order.user_id,
            "status": order.status,
            "total_price": float(order.total_price or 0),
            "created_at": order.created_at,
            "name": order.name,
            "phone": order.phone,
            "address": order.address,
            "items": item_list,
            "is_active": order.is_active
        })

    return enriched


async def get_order_details(db, order_id, user_id, is_admin=False):

    query = select(Order).where(Order.id == order_id, Order.is_active == True)
    
    if not is_admin:
        query = query.where(Order.user_id == user_id)

    result = await db.execute(query)
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
            "quantity": item.quantity,
            "price": float(item.price),
            "product": {
                "id": product.id if product else None,
                "name": product.name if product else "Unknown",
                "image": product.product_img if product else None,
                "price": float(product.price) if product else 0
            }
        })

    # Fetch User Details for Email
    user_result = await db.execute(
        select(User).where(User.id == order.user_id)
    )
    db_user = user_result.scalars().first()

    return {
        "id": order.id,
        "user_id": order.user_id,
        "user": {
            "email": db_user.email if db_user else "N/A"
        },
        "status": order.status,
        "total_price": float(order.total_price or 0),
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


async def delete_order(db, user_id, order_id):


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

    
    if order.status.lower() == "delivered":
        raise HTTPException(
            status_code=400,
            detail="Delivered orders cannot be deleted"
        )

  
    order.is_active = False

   
    result = await db.execute(
        select(OrderItems).where(
            OrderItems.order_id == order.id,
            OrderItems.is_active == True
        )
    )
    items = result.scalars().all()

    for item in items:
        item.is_active = False

    await db.commit()
    await db.refresh(order) 

    return {
        "message": "Order deleted successfully",
        "order_id": order.id,
        "is_active": order.is_active
    }



async def cancel_order(order_id , db, user_id):
    result = await db.execute(select(Order).where(Order.id == order_id,Order.user_id == user_id,Order.is_active == True))
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order Not Found")
    
    if order.status.lower() in ['cancelled', 'delivered']:
        raise HTTPException(
            status_code=400,
            detail="Cancelled or delivered orders cannot be cancelled"
        )
    
    # Restore Stock
    result = await db.execute(
        select(OrderItems).where(OrderItems.order_id == order.id, OrderItems.is_active == True)
    )
    items = result.scalars().all()
    for item in items:
        prod_result = await db.execute(
            select(Product).where(Product.id == item.product_id)
        )
        product = prod_result.scalars().first()
        if product:
            product.stock += item.quantity

    order.status = "cancelled"
    await db.commit()
    await db.refresh(order)
    return {
        "message": "Order cancelled successfully and stock restored",
        "order_id": order.id,
        "status": order.status
    }


async def get_admin_dashboard_stats(db):
    # Total Stats
    result = await db.execute(select(func.count(Order.id)).where(Order.is_active == True))
    total_orders = result.scalar() or 0

    result = await db.execute(select(func.sum(Order.total_price)).where(Order.is_active == True))
    total_revenue = result.scalar() or 0

    # Status breakdown
    result = await db.execute(
        select(Order.status, func.count(Order.id))
        .where(Order.is_active == True)
        .group_by(Order.status)
    )
    status_counts_raw = dict(result.all())
    # Normalize keys to lowercase for reliable lookup
    status_counts = {k.lower(): v for k, v in status_counts_raw.items()}

    # Monthly Sales (Last 6 months)
    month_exp = func.date_trunc('month', Order.created_at)
    result = await db.execute(
        select(month_exp.label('m'), func.sum(Order.total_price), func.count(Order.id))
        .where(Order.is_active == True)
        .group_by(month_exp)
        .order_by(month_exp.desc())
        .limit(6)
    )
    monthly_data = result.all()
    
    monthly_sales = []
    for date, revenue, count in reversed(monthly_data):
        monthly_sales.append({
            "month": date.strftime("%b %Y"),
            "revenue": float(revenue or 0),
            "orders": count
        })

    return {
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "delivered_orders": status_counts.get("delivered", 0),
        "cancelled_orders": status_counts.get("cancelled", 0),
        "pending_orders": status_counts.get("pending", 0),
        "shipped_orders": status_counts.get("shipped", 0),
        "status_pie_chart": status_counts,
        "monthly_sales_graph": monthly_sales
    }
    
