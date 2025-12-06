import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any

import requests

def _delete_on_cfbed(src: str, endpoint: str, api_token: str, proxy: str = None, is_folder: bool = False) -> bool:
    try:
        base = endpoint.rstrip('/').replace('/upload', '')
        path = src.lstrip('/')
        # 删除 API: /api/manage/delete/{path}?folder=true
        url = f"{base}/api/manage/delete/{path}"
        if is_folder:
            url += "?folder=true"
        headers = {"Authorization": f"Bearer {api_token}"}
        proxies = {"http": proxy, "https": proxy} if proxy else None
        resp = requests.delete(url, headers=headers, proxies=proxies, verify=False, timeout=60)
        return resp.status_code == 200
    except Exception:
        return False

def _perform_cleanup(account_manager):
    cfg = account_manager.config or {}
    if not cfg.get("auto_cleanup_enabled"):
        return
    endpoint = (cfg.get("upload_endpoint") or "").strip()
    api_token = (cfg.get("upload_api_token") or "").strip()
    if not endpoint or not api_token:
        return
    retention_days = int(cfg.get("upload_retention_days") or 7)
    items = cfg.get("cfbed_uploaded_files") or []
    now = datetime.utcnow()
    keep = []
    for item in items:
        try:
            created = datetime.fromisoformat(item.get("created_at"))
        except Exception:
            created = now
        if (now - created) >= timedelta(days=retention_days):
            src = item.get("src")
            proxy = cfg.get("proxy") if cfg.get("proxy_enabled") else None
            ok = _delete_on_cfbed(src, endpoint, api_token, proxy)
            if not ok:
                keep.append(item)
        else:
            keep.append(item)
    cfg["cfbed_uploaded_files"] = keep
    try:
        account_manager.save_config()
    except Exception:
        pass

def start_auto_cleanup_thread(account_manager):
    def _loop():
        while True:
            try:
                _perform_cleanup(account_manager)
            except Exception:
                pass
            time.sleep(6 * 3600)
    t = threading.Thread(target=_loop, daemon=True)
    t.start()
    return True
