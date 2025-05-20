'use client';

import { useEffect, useState, useRef } from "react";

const rows = [
  ["VIX", "SPY", "QQQ", "BTC", "DXY", "Gold", "Crude", "10Y", "5Y", "2Y", "Spread"]
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
  const containerRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/ws/global_context");
    socket.onmessage = (event) => {
      try {
        const json = JSON.parse(event.data);
        setData(json);
      } catch (err) {
        console.error("❌ Error parsing socket data", err);
      }
    };
    return () => socket.close();
  }, []);

  useEffect(() => {
    const content = contentRef.current;
    if (!content) return;

    let start = 0;
    let raf: number;

    const step = () => {
      start -= 0.3; // scroll speed (lower = slower)
      content.style.transform = `translateX(${start}px)`;

      // reset if fully scrolled
      if (Math.abs(start) >= content.scrollWidth) {
        start = containerRef.current?.offsetWidth || 0;
      }

      raf = requestAnimationFrame(step);
    };

    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, []);

  return (
    <div
      ref={containerRef}
      className="relative bg-gray-800 rounded-lg shadow-md px-4 py-2 mb-4 overflow-hidden h-[48px]"
    >
      {/* Edge fade overlays */}
      <div className="absolute top-0 left-0 h-full w-12 z-10 pointer-events-none bg-gradient-to-r from-gray-800 to-transparent" />
      <div className="absolute top-0 right-0 h-full w-12 z-10 pointer-events-none bg-gradient-to-l from-gray-800 to-transparent" />

      {/* Marquee content */}
      <div
        ref={contentRef}
        className="flex gap-3 items-center whitespace-nowrap transition-transform duration-75 will-change-transform"
      >
        {rows[0].map((key) => {
          const d = data[key] || {};
          const val = d.last ?? d.value ?? "–";
          const pct = d.pct_change !== undefined ? `${d.pct_change.toFixed(2)}%` : "";
          const arrow =
            d.arrow === "up" ? "↗" : d.arrow === "down" ? "↘" : "→";
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
              <span className={`${color} font-bold text-sm`}>{arrow}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
