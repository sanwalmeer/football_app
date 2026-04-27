from fastapi import FastAPI
from app.routes.news_routes import router as news_router

app = FastAPI()

app.include_router(news_router)