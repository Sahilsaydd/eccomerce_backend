from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.db import get_db
from app.deps.auth import get_current_user, require_role

from app.modules.order.crud import order_crud
from app.modules.order.schemas.order_schemas import OrderStatusUpdate

#  Import email functions
from app.utils.email import send_order_email, send_status_email
from app.modules.user.model.user import User
from sqlalchemy.future import select

router = APIRouter(prefix="/orders", tags=["Orders"])


#  Checkout (Create Order)
@router.post("/checkout/{product_id}")
async def checkout(
    product_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    user_id = int(user["sub"])

    #  Create order
    order = await order_crud.create_order(db, user_id, product_id)

    #  Get full user object (needed for email)
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalars().first()

    #  Send email in background
    if db_user:
        background_tasks.add_task(send_order_email, db_user, order)

    return order


#  Get user orders
@router.get("/")
async def get_orders(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    user_id = int(user["sub"])
    return await order_crud.get_orders(db, user_id)


#  Get order details
@router.get("/{order_id}")
async def get_order_details(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    user_id = int(user["sub"])
    return await order_crud.get_order_details(db, order_id, user_id)


#  ADMIN: Update Order Status
@router.put("/status/{order_id}")
async def update_status(
    order_id: int,
    data: OrderStatusUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(["admin"]))
):
    #  Update status
    result = await order_crud.update_order_status(db, order_id, data.status)

    #  Get order + user for email
    from app.modules.order.model.order_model import Order

    order_result = await db.execute(select(Order).where(Order.id == order_id))
    order = order_result.scalars().first()

    if order:
        user_result = await db.execute(select(User).where(User.id == order.user_id))
        db_user = user_result.scalars().first()

        #  Send email in background
        if db_user:
            background_tasks.add_task(send_status_email, db_user, order)

    return result