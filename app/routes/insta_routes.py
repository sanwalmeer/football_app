from fastapi import APIRouter
from app.controllers.insta_videos_controller import (
    get_all_instagram_videos,
    get_instagram_video,
    play_instagram_video
)

router = APIRouter(prefix="/instagram", tags=["Instagram Videos"])


@router.get("/videos")
def all_videos():
    return get_all_instagram_videos()


@router.get("/videos/{shortcode}")
def video_details(shortcode: str):
    return get_instagram_video(shortcode)


@router.get("/videos/play/{shortcode}")
def play_video(shortcode: str):
    return play_instagram_video(shortcode)