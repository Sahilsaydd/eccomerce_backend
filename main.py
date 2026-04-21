from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
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
origins = [
    "http://localhost:4200",
    "http://127.0.0.1:4200",   # optional but safer
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_api.router)
app.include_router(admin_api.router)
app.include_router(product_api.router)
app.include_router(cart_api.router)
app.include_router(order_api.router)