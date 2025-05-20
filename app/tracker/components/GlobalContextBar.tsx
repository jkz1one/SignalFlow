'use client';
import { useEffect, useState } from "react";

const rows = [
  ["VIX", "SPY", "QQQ", "BTC"],
  ["DXY", "Gold", "Crude"],
  ["10Y", "5Y", "2Y", "Spread"]
];

const labels: Record<string, string> = {
  VIX: "VIX",
  SPY: "SPY",
  QQQ: "QQQ",
  BTC: "BTC",
  DXY: "DXY",
  Gold: "Gold",
  Crude: "Crude",
  "10Y": "10Y",
  "5Y": "5Y",
  "2Y": "2Y",
  Spread: "Spread",
};

export default function GlobalContextBar() {
  const [data, setData] = useState<Record<string, any>>({});
  const [rowIndex, setRowIndex] = useState(0);

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/ws/global_context");
  
    socket.onopen = () => {
      console.log("🟢 Connected to global context WebSocket");
    };
  
    socket.onmessage = (event) => {
      try {
        const json = JSON.parse(event.data);
        setData(json);
      } catch (err) {
        console.error("❌ Failed to parse WebSocket message:", err);
      }
    };
  
    socket.onclose = () => {
      console.log("🔴 WebSocket closed");
    };
  
    return () => socket.close();
  }, []);
  

  const rotateRow = () => setRowIndex((rowIndex + 1) % rows.length);
  const currentRow = rows[rowIndex];

  return (
    <div className="bg-gray rounded-lg px-4 py-2 flex items-center justify-between mb-4 relative">
      {/* Invisible spacer to balance arrow width */}
      <div className="w-6" />
  
      {/* Centered ticker content */}
      <div className="flex flex-wrap justify-center items-center gap-2 flex-1 text-center">
        {currentRow.map((key) => {
          const d = data[key] || {};
          const val = d.last ?? d.value ?? "–";
          const pct = d.pct_change !== undefined ? `${d.pct_change.toFixed(2)}%` : "";
          const arrow =
            d.arrow === "up" ? "↗" :
            d.arrow === "down" ? "↘" : "→";
          const color =
            d.arrow === "up"
              ? "text-green-400"
              : d.arrow === "down"
              ? "text-red-400"
              : "text-white";
  
              return (
                <div
                  key={key}
                  className="bg-gray-700 rounded-lg px-2 py-1 flex items-center whitespace-nowrap"
                >
                  <span className={`${color} font-bold`}>{labels[key]}:&nbsp;</span>
                  <span className={`${color} font-thin text-sm`}>{val}&nbsp;</span>
                  <span className={`${color} font-bold text-sm`}>{pct}&nbsp;</span>
                  <span className={`${color} font-bold text-sm `}>{arrow}</span>
                </div>



              );              

        })}
      </div>
  
      {/* Right-aligned arrow */}
      <div
        onClick={rotateRow}
        className="ml-4 text-gray-400 text-2xl cursor-pointer select-none hover:text-white"
        title="Next Row"
      >
        ▼
      </div>
    </div>

);
  
  
}
