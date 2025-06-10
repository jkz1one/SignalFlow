from fastapi import APIRouter
from fastapi.responses import JSONResponse
import subprocess, os, json

router = APIRouter()
CACHE_DIR = "backend/cache"

@router.get("/tracker/{symbol}")
def get_tracker_data(symbol: str):
    symbol = symbol.upper()

    # Step 1: Run fetch + calc pipeline
    try:
        result = subprocess.run(
            ["python", "backend/tracker/run_tracker.py", symbol],
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Tracker pipeline failed for {symbol}",
                "stderr": e.stderr.decode() if e.stderr else "Unknown error"
            }
        )

    # Step 2: Locate output file
    path = os.path.join(CACHE_DIR, f"tracker_signals_{symbol}.json")
    if not os.path.exists(path):
        return JSONResponse(
            status_code=404,
            content={"error": f"No tracker output found for {symbol}"}
        )

    # Step 3: Load and return JSON
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to load output for {symbol}", "detail": str(e)}
        )
