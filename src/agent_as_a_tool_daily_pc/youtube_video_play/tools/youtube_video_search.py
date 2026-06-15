import aiohttp
import os
import urllib.parse
import ssl
import certifi
from autogen_core.tools import FunctionTool

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Shared across requests — context is immutable; reading certifi's CA bundle
# (~1 ms) once at import is far cheaper than doing it per call.
_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


async def search_youtube_videos(query: str) -> dict:
    """Search YouTube and return at most ONE video per query.

    Only entries that are unambiguously videos (id.kind == 'youtube#video'
    with an 11-character videoId) are returned. Channel and playlist results
    are dropped.

    Shape:
        {
          "query": "<original query>",
          "videos": [{"videoId": "<11-char id>", "title": "<title>"}]  # length 0 or 1
        }
    """
    max_results = 1
    search_url = (
        "https://www.googleapis.com/youtube/v3/search?"
        f"part=snippet&type=video&maxResults={max_results}"
        f"&q={urllib.parse.quote(query)}&key={YOUTUBE_API_KEY}"
    )
    connector = aiohttp.TCPConnector(ssl=_SSL_CONTEXT)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(search_url) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise Exception(f"YouTube search failed: {resp.status} {text}")
            data = await resp.json()

    videos = []
    for item in data.get("items", []):
        item_id = item.get("id") or {}
        if item_id.get("kind") != "youtube#video":
            continue
        video_id = item_id.get("videoId")
        if not isinstance(video_id, str) or len(video_id) != 11:
            continue
        title = (item.get("snippet") or {}).get("title", "")
        videos.append({"videoId": video_id, "title": title})

    return {"query": query, "videos": videos}


search_youtube_tool = FunctionTool(
    func=search_youtube_videos,
    name="search_youtube_videos",
    description="Search YouTube videos via the YouTube Data API v3. Returns only video results (channels and playlists are filtered out).",
)
