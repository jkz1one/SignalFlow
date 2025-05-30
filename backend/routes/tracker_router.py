# backend/routes/tracker_router.py

from fastapi import APIRouter, HTTPException
import subprocess, os, json

router = APIRouter()
CACHE_DIR = "backend/cache"

@router.get("/tracker/{symbol}")
def get_tracker_data(symbol: str):
    symbol = symbol.upper()

    # Step 1: Run fetch + calc pipeline
    result = subprocess.run(
        ["python", "backend/tracker/run_tracker.py", symbol],
        capture_output=True
    )
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr.decode())

    # Step 2: Expect fixed file path
    path = os.path.join(CACHE_DIR, f"tracker_signals_{symbol}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="No tracker output found")

    # Step 3: Return parsed JSON
    with open(path, "r") as f:
        return json.load(f)
