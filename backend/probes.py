from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os, glob, json, time
from datetime import datetime

router = APIRouter()

@router.get("/api/health")
def health():
    return {"ok": True}

# Optional: quick cache visibility
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")

def _latest(pattern: str):
    files = glob.glob(os.path.join(CACHE_DIR, pattern))
    return max(files, key=os.path.getmtime) if files else None

@router.get("/api/status")
def status():
    def brief(path):
        if not path: return None
        try:
            with open(path) as f:
                data = json.load(f)
            return {"file": os.path.basename(path), "items": len(data) if isinstance(data, (list, dict)) else None}
        except Exception as e:
            return {"file": os.path.basename(path), "error": str(e)}

    po = _latest("post_open_signals_*.json")
    en = _latest("universe_enriched_*.json")
    wl = _latest("autowatchlist_*.json")

    return JSONResponse({
        "now": datetime.now().astimezone().isoformat(),
        "tz": time.tzname,
        "cache_dir": CACHE_DIR,
        "post_open": brief(po),
        "enriched": brief(en),
        "watchlist": brief(wl),
    })
