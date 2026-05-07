from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# your routes
from app.routes.insta_routes import router as insta_router
app.include_router(insta_router)

# ✅ THIS IS REQUIRED FOR /media ACCESS
app.mount(
    "/media",
    StaticFiles(directory="media"),
    name="media"
)