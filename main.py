from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.modules.auth.api import auth_api
from app.modules.admin.api import admin_api
from app.db.database import engine
from app.db.database import Base
from app.modules.product.api import product_api
from app.modules.cart.api import cart_api
from app.modules.order.api import order_api
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown (if needed)

app = FastAPI(lifespan=lifespan)

app.include_router(auth_api.router)
app.include_router(admin_api.router)
app.include_router(product_api.router)
app.include_router(cart_api.router)
app.include_router(order_api.router)