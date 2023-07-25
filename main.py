from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import requests

app = FastAPI(
    title="Connpass Plugin API",
    description="API to get events from connpass",
    version="1.0.0",
)

ORIGINS = ["http://localhost:8000", "https://chat.openai.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/.well-known", StaticFiles(directory=".well-known"), name="static")


class Series(BaseModel):
    id: int
    title: str
    url: str


class Event(BaseModel):
    event_id: int
    title: str
    catch: str
    description: str
    event_url: str
    started_at: str
    ended_at: str
    limit: int
    hash_tag: str
    event_type: str
    accepted: int
    waiting: int
    updated_at: str
    owner_id: int
    owner_nickname: str
    owner_display_name: str
    place: str
    address: str
    lat: float
    lon: float
    series: Series


class EventField(BaseModel):
    results_start: int
    results_returned: int
    results_available: int
    events: List[Event]


@app.get("/events")
async def read_events(
    event_id: int = None,
    keyword: str = None,
    keyword_or: str = None,
    ym: str = None,
    ymd: str = None,
    nickname: str = None,
    series_id: str = None,
    start: str = None,
    order: str = None,
    count: int = None,
    format: int = None,
):
    response = requests.get(
        "https://connpass.com/api/v1/event/",
        params={
            "event_id": event_id,
            "keyword": keyword,
            "keyword_or": keyword_or,
            "ym": ym,
            "ymd": ymd,
            "nickname": nickname,
            "series_id": series_id,
            "start": start,
            "order": order,
            "count": count,
            "format": format,
        },
        headers={"User-Agent": "Mozilla/5.0"},
    )
    data = response.json()

    for event in data["events"]:
        del event["description"]
        del event["series"]
        del event["lat"]
        del event["lon"]
        del event["owner_id"]

    return data


@app.get("/openapi.yaml")
async def openapi_spec() -> Response:
    with open("openapi.yaml") as f:
        return Response(f.read(), media_type="text/yaml")


@app.get("/logo.png")
async def plugin_logo():
    return FileResponse("logo.png", media_type="image/png")
