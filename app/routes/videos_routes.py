from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter()

VIDEO_DIR = "/home/bitech-office/Sanwal/football_app/downloads"


# @router.get("/videos/{video_id}")
@router.get("/video/{video_id}")       
def get_video(video_id: str):

    file_path = os.path.join(VIDEO_DIR, f"{video_id}.mp4")

    if not os.path.exists(file_path):
        return {"error": "Video not found"}

    return FileResponse(file_path, media_type="video/mp4")