from fastapi import FastAPI
from app.routes.insta_routes import router as insta_router
app = FastAPI()

app.include_router(insta_router)