"""TikTok Content Posting API + métricas (Display API).

Credenciales (variables de entorno / secretos de GitHub):
  TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN
Ámbitos (scopes) que debe pedir la app: user.info.basic, user.info.stats, video.upload,
video.publish, video.list.

Modos:
  draft  → /v2/post/publish/inbox/video/init/  (llega a la bandeja de TikTok; el dueño pulsa publicar)
  direct → /v2/post/publish/video/init/        (publica solo; requiere app auditada por TikTok)
"""
from __future__ import annotations

import os
import time
from pathlib import Path

import requests

API = "https://open.tiktokapis.com"
AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
SCOPES = "user.info.basic,user.info.stats,video.upload,video.publish,video.list"


class TikTokError(RuntimeError):
    pass


def have_credentials() -> bool:
    return all(os.environ.get(k) for k in ("TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REFRESH_TOKEN"))


def auth_url(redirect_uri: str, state: str = "finroots") -> str:
    from urllib.parse import urlencode
    q = {"client_key": os.environ["TIKTOK_CLIENT_KEY"], "scope": SCOPES, "response_type": "code",
         "redirect_uri": redirect_uri, "state": state}
    return AUTH_URL + "?" + urlencode(q)


def exchange_code(code: str, redirect_uri: str) -> dict:
    r = requests.post(f"{API}/v2/oauth/token/", timeout=30, data={
        "client_key": os.environ["TIKTOK_CLIENT_KEY"], "client_secret": os.environ["TIKTOK_CLIENT_SECRET"],
        "code": code, "grant_type": "authorization_code", "redirect_uri": redirect_uri})
    data = r.json()
    if "access_token" not in data:
        raise TikTokError(f"OAuth: {data}")
    return data


def refresh() -> dict:
    r = requests.post(f"{API}/v2/oauth/token/", timeout=30, data={
        "client_key": os.environ["TIKTOK_CLIENT_KEY"], "client_secret": os.environ["TIKTOK_CLIENT_SECRET"],
        "grant_type": "refresh_token", "refresh_token": os.environ["TIKTOK_REFRESH_TOKEN"]})
    data = r.json()
    if "access_token" not in data:
        raise TikTokError(f"No se pudo renovar el token de TikTok: {data}")
    new_rt = data.get("refresh_token")
    if new_rt and new_rt != os.environ["TIKTOK_REFRESH_TOKEN"]:
        # El workflow lo guarda de nuevo como secreto si hay GH_PAT (ver .github/workflows).
        Path(os.environ.get("FINROOTS_NEW_REFRESH_TOKEN_FILE", ".tiktok_refresh_token")).write_text(new_rt)
    return data


def _post(path: str, token: str, json_body: dict | None = None, params: dict | None = None) -> dict:
    r = requests.post(f"{API}{path}", params=params, json=json_body or {}, timeout=60,
                      headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=UTF-8"})
    data = r.json()
    err = data.get("error", {})
    if r.status_code >= 400 or (err and err.get("code") not in (None, "ok")):
        raise TikTokError(f"{path}: HTTP {r.status_code} {err}")
    return data.get("data", {})


def _chunks(size: int) -> tuple[int, int]:
    """Reglas de TikTok: <5 MB en un trozo; si no, trozos de 5–64 MB (el último absorbe el resto)."""
    if size <= 64 * 1024 * 1024:
        return size, 1
    chunk = 10 * 1024 * 1024
    return chunk, size // chunk


def _upload(upload_url: str, video: Path, chunk: int, count: int):
    size = video.stat().st_size
    with open(video, "rb") as f:
        for i in range(count):
            start = i * chunk
            end = size - 1 if i == count - 1 else start + chunk - 1
            f.seek(start)
            body = f.read(end - start + 1)
            r = requests.put(upload_url, data=body, timeout=300, headers={
                "Content-Type": "video/mp4", "Content-Length": str(len(body)),
                "Content-Range": f"bytes {start}-{end}/{size}"})
            if r.status_code not in (200, 201, 206):
                raise TikTokError(f"Subida fallida (trozo {i+1}/{count}): HTTP {r.status_code} {r.text[:300]}")


def publish(video: Path, caption: str, cfg: dict) -> dict:
    tok = refresh()["access_token"]
    size = video.stat().st_size
    chunk, count = _chunks(size)
    source = {"source": "FILE_UPLOAD", "video_size": size, "chunk_size": chunk, "total_chunk_count": count}
    mode = cfg.get("mode", "draft")
    if mode == "direct":
        info = _post("/v2/post/publish/creator_info/query/", tok)
        opts = info.get("privacy_level_options", [])
        privacy = cfg.get("privacy_level", "PUBLIC_TO_EVERYONE")
        if privacy not in opts:
            privacy = "SELF_ONLY" if "SELF_ONLY" in opts else (opts[0] if opts else "SELF_ONLY")
        post_info = {"title": caption[:2200], "privacy_level": privacy, "disable_duet": False,
                     "disable_comment": False, "disable_stitch": False, "video_cover_timestamp_ms": 1200}
        if cfg.get("ai_generated_label", True):
            post_info["is_aigc"] = True
        data = _post("/v2/post/publish/video/init/", tok, {"post_info": post_info, "source_info": source})
    else:
        data = _post("/v2/post/publish/inbox/video/init/", tok, {"source_info": source})
    _upload(data["upload_url"], video, chunk, count)
    pid = data["publish_id"]
    status = {}
    for _ in range(30):
        time.sleep(6)
        status = _post("/v2/post/publish/status/fetch/", tok, {"publish_id": pid})
        if status.get("status") in ("PUBLISH_COMPLETE", "SEND_TO_USER_INBOX", "FAILED"):
            break
    if status.get("status") == "FAILED":
        raise TikTokError(f"TikTok rechazó el vídeo: {status.get('fail_reason')}")
    return {"publish_id": pid, "mode": mode, "status": status.get("status"),
            "post_ids": status.get("publicaly_available_post_id") or status.get("publicly_available_post_id")}


def metrics(max_videos: int = 20) -> dict:
    """Seguidores y estadísticas de los últimos vídeos de la cuenta."""
    tok = refresh()["access_token"]
    r = requests.get(f"{API}/v2/user/info/", timeout=30, headers={"Authorization": f"Bearer {tok}"},
                     params={"fields": "open_id,display_name,follower_count,following_count,likes_count,video_count"})
    user = r.json().get("data", {}).get("user", {})
    vids = _post("/v2/video/list/", tok, {"max_count": max_videos},
                 params={"fields": "id,title,create_time,duration,view_count,like_count,comment_count,share_count"})
    return {"user": user, "videos": vids.get("videos", []), "fetched_at": int(time.time())}
