import re
import json
import html
import random
import asyncio
import urllib.parse
import httpx
from bs4 import BeautifulSoup
from app.config import logger

SEMAPHORE = asyncio.Semaphore(3)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7",
    "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1"
}

def parse_title_artist_fallback(raw_title: str, site_name: str = "") -> tuple[str, str]:
    if not raw_title:
        return ("Unknown Title", site_name.strip() or "Unknown Artist")
    
    title = "Unknown Title"
    artist = site_name.strip() or "Unknown Artist"
    
    if ", by " in raw_title:
        parts = raw_title.split(", by ", 1)
        title, artist = parts[0].strip(), parts[1].strip()
    elif " - " in raw_title:
        parts = raw_title.split(" - ", 1)
        artist, title = parts[0].strip(), parts[1].strip()
    elif " by " in raw_title:
        parts = raw_title.rsplit(" by ", 1)
        title, artist = parts[0].strip(), parts[1].strip()
    elif " | " in raw_title:
        parts = raw_title.split(" | ", 1)
        title, artist = parts[0].strip(), parts[1].strip()
    else:
        title = raw_title.strip()

    if (not artist or artist == "Unknown Artist") and site_name:
        artist = site_name.strip()

    return (title or "Unknown Title", artist or "Unknown Artist")

def unwrap_bandcamp_url(raw_url: str) -> str:
    if not raw_url:
        return ""
    curr = raw_url
    for _ in range(2):
        if "%" in curr:
            curr = urllib.parse.unquote(curr)
            
    m = re.search(r'(?:url|q|dest|target|redirect)=((?:https?%3A%2F%2F|https?://)[^&]+)', raw_url, re.IGNORECASE)
    if m:
        target = m.group(1)
        for _ in range(2):
            if "%" in target:
                target = urllib.parse.unquote(target)
        curr = target
        
    if "email_redirect" in curr and not ("/album/" in curr or "/track/" in curr):
        return curr
        
    clean = curr.split("?")[0].strip().rstrip("/")
    return clean

async def scrape_bandcamp_metadata(url: str) -> dict:
    clean_url = unwrap_bandcamp_url(url)
    fallback_data = {
        "url": clean_url,
        "title": "Bandcamp Release",
        "artist": "Various Artists",
        "cover_image_url": "",
        "entity_type": "album" if "/album/" in clean_url else "track",
        "entity_id": "",
        "stream_url": "",
        "tracks_json": "[]"
    }

    async with SEMAPHORE:
        await asyncio.sleep(random.uniform(0.4, 0.9))
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(timeout=12.0, follow_redirects=True, headers=HEADERS) as client:
                    resp = await client.get(clean_url)
                    if resp.status_code != 200:
                        continue
                    
                    html_text = resp.text
                    soup = BeautifulSoup(html_text, "html.parser")
                    final_url = str(resp.url).split("?")[0].rstrip("/")
                    
                    # 1. 廠牌獨立網域驗證
                    meta_bc = soup.find("meta", {"name": "bc-page-properties"})
                    meta_site = soup.find("meta", {"property": "og:site_name"})
                    is_bc = meta_bc is not None or (meta_site and "bandcamp" in meta_site.get("content", "").lower())
                    
                    if not is_bc and "bandcamp.com" not in final_url:
                        logger.warning(f"跳過非 Bandcamp 獨立網域: {final_url}")
                        return None
                    
                    # 2. 深度讀取 TralbumData JSON
                    tralbum_data = None
                    m_tralbum = re.search(r'var\s+TralbumData\s*=\s*(\{.*?\});\s*(?:var|</script>)', html_text, re.DOTALL)
                    if not m_tralbum:
                        m_tralbum = re.search(r'data-tralbum="([^"]+)"', html_text)
                    if m_tralbum:
                        try:
                            raw_json = html.unescape(m_tralbum.group(1))
                            tralbum_data = json.loads(raw_json)
                        except Exception as e:
                            logger.warning(f"TralbumData 解析異常: {e}")

                    # 3. 標題與藝人解析
                    title = "Unknown Title"
                    artist = "Unknown Artist"
                    
                    if tralbum_data and isinstance(tralbum_data.get("current"), dict):
                        curr = tralbum_data["current"]
                        if curr.get("title"):
                            title = curr["title"]
                        if curr.get("artist"):
                            artist = curr["artist"]
                    if (artist == "Unknown Artist" or not artist) and tralbum_data and tralbum_data.get("artist"):
                        artist = tralbum_data["artist"]

                    if title == "Unknown Title" or artist == "Unknown Artist":
                        meta_title = soup.find("meta", {"property": "og:title"})
                        site_name = meta_site.get("content", "").strip() if meta_site and meta_site.get("content") else ""
                        if meta_title and meta_title.get("content"):
                            fb_title, fb_artist = parse_title_artist_fallback(meta_title["content"], site_name)
                            if title == "Unknown Title":
                                title = fb_title
                            if not artist or artist == "Unknown Artist":
                                artist = fb_artist
                        elif (not artist or artist == "Unknown Artist") and site_name:
                            artist = site_name

                    # 4. 封面圖片
                    cover_url = ""
                    meta_img = soup.find("meta", {"property": "og:image"})
                    if meta_img:
                        cover_url = meta_img.get("content", "")
                    elif tralbum_data and tralbum_data.get("art_id"):
                        cover_url = f"https://f4.bcbits.com/img/a{tralbum_data['art_id']}_5.jpg"
                    
                    # 5. 精確提取 Entity Type、ID、多音軌清單與 MP3 串流
                    entity_type = "album" if "/album/" in final_url else "track"
                    entity_id = ""
                    stream_url = ""
                    tracks_list = []

                    if tralbum_data:
                        if tralbum_data.get("item_type") in ["a", "album"]:
                            entity_type = "album"
                        elif tralbum_data.get("item_type") in ["t", "track"]:
                            entity_type = "track"
                            
                        if tralbum_data.get("item_id"):
                            entity_id = str(tralbum_data["item_id"])
                        elif tralbum_data.get("id"):
                            entity_id = str(tralbum_data["id"])
                        elif tralbum_data.get("current", {}).get("id"):
                            entity_id = str(tralbum_data["current"]["id"])
                            
                        trackinfo = tralbum_data.get("trackinfo", [])
                        for idx, t in enumerate(trackinfo, 1):
                            t_stream = ""
                            files = t.get("file") or {}
                            if isinstance(files, dict):
                                for k, v in files.items():
                                    if isinstance(v, str) and v.startswith("http"):
                                        t_stream = v
                                        break
                            if not stream_url and t_stream:
                                stream_url = t_stream
                            tracks_list.append({
                                "track_num": t.get("track_num") or idx,
                                "title": t.get("title", f"Track {idx}"),
                                "duration": t.get("duration", 0),
                                "stream_url": t_stream,
                                "entity_id": str(t.get("id", ""))
                            })

                    if not tracks_list:
                        tracks_list.append({
                            "track_num": 1,
                            "title": title,
                            "duration": 0,
                            "stream_url": stream_url,
                            "entity_id": entity_id
                        })

                    # 備用：讀取 bc-page-properties
                    if not entity_id and meta_bc and meta_bc.get("content"):
                        try:
                            props = json.loads(meta_bc["content"])
                            item_t = props.get("item_type")
                            if item_t in ["a", "album"]:
                                entity_type = "album"
                            elif item_t in ["t", "track"]:
                                entity_type = "track"
                            if props.get("item_id"):
                                entity_id = str(props["item_id"])
                        except Exception:
                            pass

                    # 備用：讀取 og:video
                    if not entity_id:
                        meta_video = soup.find("meta", {"property": "og:video"})
                        if meta_video and meta_video.get("content"):
                            v_content = meta_video["content"]
                            m_embed = re.search(r'(album|track)=(\d+)', v_content)
                            if m_embed:
                                entity_type = m_embed.group(1)
                                entity_id = m_embed.group(2)

                    return {
                        "url": final_url,
                        "title": title,
                        "artist": artist,
                        "cover_image_url": cover_url,
                        "entity_type": entity_type,
                        "entity_id": entity_id,
                        "stream_url": stream_url,
                        "tracks_json": json.dumps(tracks_list, ensure_ascii=False)
                    }
            except Exception as ex:
                logger.warning(f"爬取 {clean_url} 異常 (嘗試 {attempt + 1}/2): {ex}")
                await asyncio.sleep(1.0)
    
    logger.error(f"啟用佔位卡片降級寫入: {clean_url}")
    return fallback_data
