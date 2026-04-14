from fastapi import FastAPI
from app.modules.auth.api import  auth_api
from app.modules.admin.api import admin_api
from app.db.database import engine
from app.db.database import Base
from app.modules.product.api import product_api

app = FastAPI()
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth_api.router)
app.include_router(admin_api.router)
app.include_router(product_api.router)