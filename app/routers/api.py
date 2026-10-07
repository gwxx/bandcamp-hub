import io
import csv
import json
import sqlite3
import httpx
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel, Field
from app.config import CREDENTIALS_PATH, TOKEN_PATH, DB_PATH
from app.database import backup_and_reset_database, get_db_connection
from app.services.gmail_service import get_oauth_flow, get_credentials, disconnect_account
from app.services.sync_pipeline import run_sync_pipeline
from app.services.scraper_service import scrape_bandcamp_metadata

router = APIRouter(prefix="/api")

def get_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

class ResetRequest(BaseModel):
    confirmation: str

class BulkListenedRequest(BaseModel):
    release_ids: list[int] | None = None
    iso_week: str | None = None

class BpmUpdateRequest(BaseModel):
    bpm: float | None = None

    def validate_bpm_range(self):
        if self.bpm is not None and (self.bpm < 40.0 or self.bpm > 300.0):
            raise HTTPException(status_code=400, detail="BPM 數值必須在合理範圍內 (40.0 ~ 300.0)")


@router.get("/auth/status")
def auth_status():
    return {
        "has_credentials": CREDENTIALS_PATH.exists(),
        "is_connected": get_credentials() is not None
    }

@router.post("/auth/upload-credentials")
async def upload_credentials(file: UploadFile = File(...)):
    content = await file.read()
    try:
        data = json.loads(content)
        if not ("installed" in data or "web" in data):
            raise ValueError("缺少 installed 或 web 用戶端節點")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"無效的 OAuth 憑證 JSON: {e}")
    with open(CREDENTIALS_PATH, "wb") as f:
        f.write(content)
    return {"status": "ok", "message": "憑證上傳成功"}

@router.get("/auth/url")
def get_auth_url(port: int = Query(8000)):
    redirect_uri = f"http://127.0.0.1:{port}/api/auth/callback"
    flow = get_oauth_flow(redirect_uri)
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline", include_granted_scopes="true")
    return {"auth_url": auth_url}

@router.get("/auth/callback")
def auth_callback(code: str, port: int = 8000):
    redirect_uri = f"http://127.0.0.1:{port}/api/auth/callback"
    flow = get_oauth_flow(redirect_uri)
    flow.fetch_token(code=code)
    creds = flow.credentials
    with open(TOKEN_PATH, "w", encoding="utf-8") as f:
        f.write(creds.to_json())
    return Response(content="<script>window.opener ? window.opener.location.reload() : window.location.href='/'; window.close();</script>", media_type="text/html")

@router.post("/auth/disconnect")
def disconnect():
    disconnect_account()
    return {"status": "ok"}

@router.get("/sync/stream")
async def sync_stream(force_rescan: bool = False, limit: int = 50):
    effective_limit = 200 if force_rescan else min(200, max(1, limit))
    return StreamingResponse(run_sync_pipeline(force_rescan=force_rescan, limit=effective_limit), media_type="text/event-stream")

@router.get("/releases")
def get_releases(response: Response, filter: str = "all", q: str = "", limit_weeks: int = 12):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    with get_db_connection() as conn:
        cur = conn.cursor()
        
        sql = "SELECT * FROM releases WHERE 1=1"
        params = []
        
        if filter == "unlistened":
            sql += " AND is_listened = 0"
        elif filter == "starred":
            sql += " AND is_starred = 1"
            
        if q.strip():
            sql += " AND (title LIKE ? OR artist LIKE ?)"
            keyword = f"%{q.strip()}%"
            params.extend([keyword, keyword])
            
        sql += " ORDER BY iso_week DESC, is_listened ASC, id DESC"
        cur.execute(sql, params)
        rows = [dict(r) for r in cur.fetchall()]

    weeks_map = {}
    for r in rows:
        w = r["iso_week"]
        if w not in weeks_map:
            weeks_map[w] = []
            
        try:
            r["tracks"] = json.loads(r.get("tracks_json") or "[]")
        except Exception:
            r["tracks"] = []
        if not r["tracks"] and r.get("stream_url"):
            r["tracks"] = [{
                "track_num": 1,
                "title": r["title"],
                "duration": 0,
                "stream_url": r["stream_url"],
                "entity_id": r.get("entity_id") or ""
            }]
            
        weeks_map[w].append(r)

    all_weeks = list(weeks_map.keys())
    total_weeks = len(all_weeks)
    
    if not q.strip() and filter != "starred":
        all_weeks = all_weeks[:limit_weeks]

    result = [{"week": w, "releases": weeks_map[w]} for w in all_weeks if w in weeks_map]
    return {
        "weeks": result,
        "total_weeks": total_weeks,
        "displayed_weeks": len(result)
    }

@router.patch("/releases/{release_id}/listened")
def toggle_listened(release_id: int):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT is_listened, is_starred FROM releases WHERE id = ?;", (release_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Release not found")
        new_listened = 1 - row["is_listened"]
        now_iso = get_now_iso()
        # ADR 0004: Marking as unlistened retains is_starred
        conn.execute("UPDATE releases SET is_listened = ?, updated_at = ? WHERE id = ?;", (new_listened, now_iso, release_id))
        conn.commit()
    return {"status": "ok", "is_listened": new_listened, "is_starred": row["is_starred"]}

@router.patch("/releases/{release_id}/star")
def toggle_star(release_id: int):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT is_starred, is_listened FROM releases WHERE id = ?;", (release_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Release not found")
        new_starred = 1 - row["is_starred"]
        now_iso = get_now_iso()
        
        if new_starred == 1:
            # ADR 0004: Starring (0 -> 1) implicitly promotes is_listened = 1
            conn.execute("UPDATE releases SET is_starred = 1, is_listened = 1, updated_at = ? WHERE id = ?;", (now_iso, release_id))
            new_listened = 1
        else:
            # ADR 0004: Unstarring (1 -> 0) retains is_listened state
            conn.execute("UPDATE releases SET is_starred = 0, updated_at = ? WHERE id = ?;", (now_iso, release_id))
            new_listened = row["is_listened"]
            
        conn.commit()
    return {"status": "ok", "is_starred": new_starred, "is_listened": new_listened}

@router.post("/releases/bulk-listened")
def bulk_listened(payload: BulkListenedRequest):
    now_iso = get_now_iso()
    with get_db_connection() as conn:
        if payload.release_ids:
            placeholders = ",".join("?" for _ in payload.release_ids)
            conn.execute(
                f"UPDATE releases SET is_listened = 1, updated_at = ? WHERE id IN ({placeholders});",
                [now_iso] + payload.release_ids
            )
        elif payload.iso_week:
            conn.execute(
                "UPDATE releases SET is_listened = 1, updated_at = ? WHERE iso_week = ?;",
                (now_iso, payload.iso_week)
            )
        conn.commit()
    return {"status": "ok"}


@router.get("/export/csv")
def export_csv(filter: str = "starred"):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ISO_Week", "Artist", "Title", "Bandcamp_URL", "BPM", "Key", "Is_Starred", "Is_Listened", "First_Synced_At"])
    
    with get_db_connection() as conn:
        sql = "SELECT * FROM releases"
        if filter == "starred":
            sql += " WHERE is_starred = 1"
        sql += " ORDER BY iso_week DESC, id DESC;"
        
        for r in conn.execute(sql):
            writer.writerow([
                r["iso_week"], r["artist"], r["title"], r["url"],
                r["bpm"] or "", r["key"] or "",
                r["is_starred"], r["is_listened"], r["first_synced_at"]
            ])
            
    output.seek(0)
    filename = f"bandcamp_{filter}_{datetime.now().strftime('%Y%m%d')}.csv"
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/database/reset")
def reset_db(payload: ResetRequest):
    if payload.confirmation.strip() != "RESET":
        raise HTTPException(status_code=400, detail="請手動輸入 RESET 確認重設。")
    backup_name = backup_and_reset_database()
    return {"status": "ok", "backup": backup_name}


@router.patch("/releases/{release_id}/bpm")
def update_bpm(release_id: int, payload: BpmUpdateRequest):
    payload.validate_bpm_range()
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM releases WHERE id = ?;", (release_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Release not found")
        now_iso = get_now_iso()
        conn.execute("UPDATE releases SET bpm = ?, updated_at = ? WHERE id = ?;", (payload.bpm, now_iso, release_id))
        conn.commit()
    return {"status": "ok", "id": release_id, "bpm": payload.bpm}


@router.post("/releases/{release_id}/refresh-stream")
async def refresh_stream(release_id: int):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, url, title, artist FROM releases WHERE id = ?;", (release_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Release not found")
        rel_url = row["url"]

    meta = await scrape_bandcamp_metadata(rel_url)
    if not meta:
        raise HTTPException(status_code=502, detail="無法自 Bandcamp 擷取最新串流資料")

    stream_url = meta.get("stream_url", "")
    tracks_json = meta.get("tracks_json", "[]")
    cover_image_url = meta.get("cover_image_url", "")
    now_iso = get_now_iso()

    with get_db_connection() as conn:
        conn.execute("""
            UPDATE releases
            SET stream_url = ?,
                tracks_json = ?,
                cover_image_url = CASE WHEN ? != '' THEN ? ELSE cover_image_url END,
                updated_at = ?
            WHERE id = ?;
        """, (stream_url, tracks_json, cover_image_url, cover_image_url, now_iso, release_id))
        conn.commit()

    try:
        tracks = json.loads(tracks_json)
    except Exception:
        tracks = []

    return {
        "status": "ok",
        "id": release_id,
        "stream_url": stream_url,
        "tracks": tracks
    }


@router.get("/releases/{release_id}/stream-proxy")
async def stream_proxy(release_id: int, track_index: int = 0):
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, stream_url, tracks_json FROM releases WHERE id = ?;", (release_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Release not found")

    target_url = row["stream_url"]
    if row["tracks_json"]:
        try:
            tracks = json.loads(row["tracks_json"])
            if 0 <= track_index < len(tracks) and tracks[track_index].get("stream_url"):
                target_url = tracks[track_index]["stream_url"]
        except Exception:
            pass

    if not target_url:
        raise HTTPException(status_code=404, detail="No audio stream available")

    async def audio_streamer():
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            async with client.stream("GET", target_url) as resp:
                if resp.status_code >= 400:
                    raise HTTPException(status_code=resp.status_code, detail="Upstream stream fetch failed")
                async for chunk in resp.aiter_bytes(chunk_size=65536):
                    yield chunk

    return StreamingResponse(
        audio_streamer(),
        media_type="audio/mpeg",
        headers={
            "Accept-Ranges": "bytes",
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "public, max-age=3600"
        }
    )

