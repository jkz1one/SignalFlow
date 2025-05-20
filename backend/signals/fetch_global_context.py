# backend/routes/fetch_global_context.py

from fastapi import WebSocket, APIRouter, WebSocketDisconnect
import yfinance as yf
from datetime import datetime
from pytz import timezone
import pandas as pd
import asyncio
import json

router = APIRouter()

symbols = {
    "SPY": "SPY",
    "QQQ": "QQQ",
    "VIX": "^VIX",    
    "BTC": "BTC-USD",
    "DXY": "DX-Y.NYB",
    "Gold": "GC=F",
    "Crude": "CL=F",
    "10Y": "^TNX",
    "5Y": "^FVX",
    "2Y": "^IRX",
}

def build_global_context():
    eastern = timezone("US/Eastern")
    context = {"timestamp": datetime.now(eastern).isoformat()}
    for label, ticker in symbols.items():
        try:
            df = yf.download(ticker, period="1d", interval="1m", progress=False, auto_adjust=False)
            if df.empty:
                raise ValueError("No data returned")

            open_price = df["Open"].iloc[0].item()
            last_price = df["Close"].iloc[-1].item()

            if open_price == 0 or pd.isna(open_price):
                pct = 0
            else:
                pct = ((last_price - open_price) / open_price) * 100

            context[label] = {
                "last": round(last_price, 2),
                "open": round(open_price, 2),
                "pct_change": round(pct, 2),
                "arrow": "up" if pct > 0 else "down" if pct < 0 else "flat"
            }

        except Exception as e:
            context[label] = {"error": str(e)}


    # Spread logic
    try:
        ten_y = context.get("10Y", {}).get("last")
        two_y = context.get("2Y", {}).get("last")
        if isinstance(ten_y, (int, float)) and isinstance(two_y, (int, float)):
            spread = round(ten_y * 0.1 - two_y / 100, 2)
            context["Spread"] = {
                "value": spread,
                "arrow": "up" if spread > 0 else "down" if spread < 0 else "flat"
            }
    except Exception as e:
        context["Spread"] = {"error": f"Spread calc failed: {e}"}

    return context

@router.websocket("/ws/global_context")
async def stream_context(websocket: WebSocket):
    await websocket.accept()
    print("✅ WebSocket client connected")

    try:
        while True:
            context = build_global_context()

            # ✅ Save snapshot to disk
            try:
                with open("backend/cache/global_context.json", "w") as f:
                    json.dump(context, f, indent=2)
                print("✅ Saved global_context.json")
            except Exception as e:
                print(f"❌ Failed to write global_context.json: {e}")

            # ✅ Push to WebSocket
            try:
                await websocket.send_text(json.dumps(context))
            except Exception as e:
                print(f"❌ Failed to send update: {e}")
                return  # client disconnected

            await asyncio.sleep(60)
    except WebSocketDisconnect:
        print("🔌 WebSocket client disconnected")
    except Exception as e:
        print(f"❌ WebSocket crashed: {e}")