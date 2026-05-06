from fastapi import APIRouter
from app.controllers.news_controller import (
    get_all_news,
    get_news_by_id,
    get_all_videos,
    get_video_by_id,
    get_all_teams,
    get_team_by_id,
    get_all_matches,
    get_match_by_id,
    get_all_leagues,
    get_league_by_id,
    get_news_count
)
router = APIRouter()



@router.get("/news/count")
def news_count():
    return {"total": get_news_count()}

@router.get("/news")
def fetch_news():
    return get_all_news()

@router.get("/news/{news_id}")
def fetch_single_news(news_id: int):
    data = get_news_by_id(news_id)

    if not data:
        return {"error": "News not found"}

    return data



@router.get("/videos")
def fetch_videos():
    return get_all_videos()


@router.get("/videos/{video_id}")
def fetch_single_video(video_id: int):
    data = get_video_by_id(video_id)

    if not data:
        return {"error": "Video not found"}

    return data

@router.get("/teams")
def fetch_teams():
    return get_all_teams()


@router.get("/teams/{team_id}")
def fetch_team(team_id: int):
    data = get_team_by_id(team_id)

    if not data:
        return {"error": "Team not found"}

    return data

@router.get("/matches")
def fetch_matches():
    return get_all_matches()


@router.get("/matches/{match_id}")
def fetch_match(match_id: int):
    data = get_match_by_id(match_id)

    if not data:
        return {"error": "Match not found"}

    return data

@router.get("/leagues")
def fetch_leagues():
    return get_all_leagues()


@router.get("/leagues/{league_id}")
def fetch_league(league_id: int):
    data = get_league_by_id(league_id)
    if not data:
        return {"error": "League not found"}
    return data

