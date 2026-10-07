import re
import json
import base64
import asyncio
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from app.config import DB_PATH, logger
from app.database import get_db_connection
from app.services.gmail_service import build_gmail_service, disconnect_account
from app.services.scraper_service import scrape_bandcamp_metadata, unwrap_bandcamp_url

SYNC_LOCK = asyncio.Lock()

def fetch_messages_paginated(service, query: str, max_cap: int = 200) -> list[dict]:
    all_messages = []
    page_token = None
    while len(all_messages) < max_cap:
        page_size = min(50, max_cap - len(all_messages))
        req = service.users().messages().list(userId="me", q=query, maxResults=page_size, pageToken=page_token)
        resp = req.execute()
        msgs = resp.get("messages", [])
        if not msgs:
            break
        all_messages.extend(msgs)
        if len(all_messages) >= max_cap:
            break
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return all_messages[:max_cap]

def extract_email_html(payload: dict) -> str:
    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/html":
                raw = part.get("body", {}).get("data", "")
                if raw:
                    return base64.urlsafe_b64decode(raw).decode("utf-8", errors="ignore")
    elif "body" in payload and payload["body"].get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="ignore")
    return ""

def compute_iso_week_utc(internal_timestamp: float) -> str:
    msg_dt = datetime.fromtimestamp(internal_timestamp, tz=timezone.utc)
    iso_year, iso_week, _ = msg_dt.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"

async def run_sync_pipeline(force_rescan: bool = False, limit: int = 50):
    if SYNC_LOCK.locked():
        yield f"data: {json.dumps({'status': 'conflict', 'message': '同步作業已在執行中'})}\n\n"
        return

    effective_limit = 200 if force_rescan else min(200, max(1, limit))

    async with SYNC_LOCK:
        service = build_gmail_service()
        if not service:
            yield f"data: {json.dumps({'status': 'auth_expired', 'message': 'Gmail 尚未授權或授權已過期'})}\n\n"
            return

        yield f"data: {json.dumps({'status': 'start', 'message': '正在連線 Gmail 查詢發行通知...'})}\n\n"
        
        query = 'from:(Bandcamp OR "noreply@bandcamp.com") ("New Release" OR "released" OR "out now" OR "pre-order") -merch -"t-shirt" -receipt -purchased -community -ticket -campaign'
        
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT last_successful_sync FROM sync_watermark WHERE id = 1;")
            row = cur.fetchone()
            watermark = row[0] if (row and not force_rescan) else None

        if watermark:
            query += f" after:{watermark}"
        else:
            query += " newer_than:30d"

        try:
            messages = await asyncio.to_thread(fetch_messages_paginated, service, query, effective_limit)
        except Exception as e:
            logger.error(f"Gmail API 查詢異常: {e}")
            if "invalid_grant" in str(e).lower() or "401" in str(e):
                disconnect_account()
                yield f"data: {json.dumps({'status': 'auth_expired', 'message': 'Google 授權已失效，請重新連結'})}\n\n"
            else:
                yield f"data: {json.dumps({'status': 'error', 'message': f'Gmail 查詢失敗: {e}'})}\n\n"
            return

        total_msgs = len(messages)
        yield f"data: {json.dumps({'status': 'progress', 'current': 0, 'total': total_msgs, 'message': f'發現 {total_msgs} 封候選通知信件'})}\n\n"
        
        if total_msgs == 0:
            yield f"data: {json.dumps({'status': 'complete', 'added': 0, 'message': '信箱已是最新狀態，無新發行'})}\n\n"
            return

        added_count = 0
        now_iso = datetime.now(timezone.utc).isoformat()
        
        for idx, msg_meta in enumerate(messages, 1):
            try:
                mid = msg_meta["id"]
                msg = await asyncio.to_thread(lambda: service.users().messages().get(userId="me", id=mid, format="full").execute())
                internal_date = int(msg.get("internalDate", 0)) / 1000.0
                iso_week = compute_iso_week_utc(internal_date)
                
                body_html = extract_email_html(msg.get("payload", {}))

                soup = BeautifulSoup(body_html, "html.parser")
                candidate_urls = set()
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    clean_url = unwrap_bandcamp_url(href)
                    if not clean_url:
                        continue
                    if ("/album/" in clean_url or "/track/" in clean_url or "email_redirect" in clean_url) and not any(x in clean_url for x in ["/merch", "/community", "/feed", "/subscribe"]):
                        candidate_urls.add(clean_url)

                for url in candidate_urls:
                    meta = await scrape_bandcamp_metadata(url)
                    if not meta:
                        continue
                    
                    with get_db_connection() as conn:
                        conn.execute("""
                        INSERT INTO releases (url, title, artist, cover_image_url, entity_type, entity_id, stream_url, tracks_json, iso_week, first_synced_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(url) DO UPDATE SET
                            title = excluded.title,
                            artist = excluded.artist,
                            cover_image_url = excluded.cover_image_url,
                            entity_type = excluded.entity_type,
                            entity_id = excluded.entity_id,
                            stream_url = excluded.stream_url,
                            tracks_json = excluded.tracks_json,
                            updated_at = excluded.updated_at;
                        """, (
                            meta["url"], meta["title"], meta["artist"], meta["cover_image_url"],
                            meta["entity_type"], meta["entity_id"], meta.get("stream_url", ""),
                            meta.get("tracks_json", "[]"), iso_week, now_iso, now_iso
                        ))
                        conn.commit()
                        added_count += 1
            except Exception as ex:
                logger.error(f"信件 {msg_meta['id']} 處理異常: {ex}")

            yield f"data: {json.dumps({'status': 'progress', 'current': idx, 'total': total_msgs, 'message': f'正在處理第 {idx}/{total_msgs} 封信件...'})}\n\n"

        new_watermark = str(int(datetime.now(timezone.utc).timestamp()))
        with get_db_connection() as conn:
            conn.execute("""
            INSERT INTO sync_watermark (id, last_successful_sync, updated_at)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                last_successful_sync = excluded.last_successful_sync,
                updated_at = excluded.updated_at;
            """, (new_watermark, now_iso))
            conn.commit()

        if total_msgs >= effective_limit and not force_rescan:
            complete_msg = f"同步完成！已收納/更新 {added_count} 部作品（已達單次上限 {effective_limit} 封；若需補齊更早歷史可至設定執行強制重掃）"
        else:
            complete_msg = f"同步完成！已收納/更新 {added_count} 部作品"

        yield f"data: {json.dumps({'status': 'complete', 'added': added_count, 'message': complete_msg})}\n\n"

