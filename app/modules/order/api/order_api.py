from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.db import get_db
from app.deps.auth import get_current_user, require_role

from app.modules.order.crud import order_crud
from app.modules.order.model.order_model import Order
from app.modules.order.schemas.order_schemas import OrderCreate, OrderStatusUpdate

from app.utils.email import send_order_email, send_status_email
from app.modules.user.model.user import User
from sqlalchemy.future import select

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/checkout/{product_id}")
async def checkout(
    product_id: int,
    data:OrderCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    user_id = int(user["sub"])

    order = await order_crud.create_order(db, user_id, product_id, data)

    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalars().first()

    if db_user:
        background_tasks.add_task(send_order_email, db_user, order)

    return order


@router.get("/")
async def get_orders(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    user_id = int(user["sub"])
    role = user.get("role")

    if role == "admin":
        return await order_crud.get_orders(db, is_admin=True)

    return await order_crud.get_orders(db, user_id=user_id)

@router.get("/{order_id}")
async def get_order_details(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    user_id = int(user["sub"])
    return await order_crud.get_order_details(db, order_id, user_id)


@router.put("/status/{order_id}")
async def update_status(
    order_id: int,
    data: OrderStatusUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role(["admin"]))
):
    result = await order_crud.update_order_status(db, order_id, data.status)

    from app.modules.order.model.order_model import Order

    order_result = await db.execute(select(Order).where(Order.id == order_id))
    order = order_result.scalars().first()

    if order:
        user_result = await db.execute(select(User).where(User.id == order.user_id))
        db_user = user_result.scalars().first()

        if db_user:
            background_tasks.add_task(send_status_email, db_user, order)

    return result


@router.delete("/delete/{order_id}")
async def delete_order(order_id:int ,db:AsyncSession = Depends(get_db),user=Depends(get_current_user)):
    user_id = int(user["sub"])
    return await order_crud.delete_order(db ,user_id,order_id)

@router.put("/cancel/{order_id}")
async def cancel_order(order_id:int ,db:AsyncSession = Depends(get_db),user=Depends(get_current_user)):
    user_id = int(user["sub"])
    return await order_crud.cancel_order(order_id, db, user_id)