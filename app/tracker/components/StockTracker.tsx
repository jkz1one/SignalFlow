"use client";

import { useEffect, useState } from "react";

type TrackerData = {
  symbol: string;
  timestamp: string;
  momentum: string;
  system_30m: string;
  system_1h: string;
  premarket_high: number;
  premarket_low: number;
  prev_day_high: number;
  prev_day_low: number;
  prev_day_close: number;
  current_price?: number;
};

export default function StockTracker() {
  const [symbol, setSymbol] = useState<string>(() =>
    typeof window !== "undefined" ? localStorage.getItem("symbol_tracker") || "SPY" : "SPY"
  );
  const [input, setInput] = useState(symbol);
  const [data, setData] = useState<TrackerData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Format numbers cleanly
  const formatNum = (val: number | undefined) =>
    val !== undefined ? val.toFixed(2) : "–";

  // Color-coding for momentum/system states
  const getColor = (val: string) => {
    if (val === "Bullish") return "text-green-400";
    if (val === "Bearish") return "text-red-400";
    if (val === "Chop" || val === "Neutral") return "text-yellow-300";
    return "text-white";
  };

  useEffect(() => {
    async function fetchTracker() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`/api/tracker/${symbol}`);
        if (!res.ok) throw new Error("Failed to fetch tracker data");
        const json = await res.json();
        setData(json);
        localStorage.setItem("symbol_tracker", symbol);
      } catch {
        setError("Error loading data");
        setData(null);
      } finally {
        setLoading(false);
      }
    }

    fetchTracker();
    const interval = setInterval(fetchTracker, 60000); // Refresh every 60s
    return () => clearInterval(interval);
  }, [symbol]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) setSymbol(input.trim().toUpperCase());
  };

  return (
    <div className="bg-gray-800 p-4 rounded-2xl w-full max-w-4xl mx-auto space-y-4 shadow-lg">
      {/* Search */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          className="bg-gray-700 text-white px-3 py-2 rounded-md w-32"
          value={input}
          onChange={(e) => setInput(e.target.value.toUpperCase())}
          placeholder="Enter ticker"
        />
        <button
          type="submit"
          disabled={loading || input === symbol}
          className="bg-gray-700 text-white px-3 py-2 border border-gray-600 rounded-md w-32 focus:outline-none focus:ring-2 focus:ring-green-400 disabled:opacity-50"
        >
          {loading ? "Loading..." : "Search"}
        </button>
      </form>

      {error && <p className="text-red-400">{error}</p>}

      {data && (
        <>
          <div className="text-right text-xs text-gray-400">
            Updated: {new Date(data.timestamp).toLocaleTimeString()}
          </div>

          {/* Row 1 */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="bg-gray-700 rounded-lg p-4 text-center">
              <h3 className="text-sm text-gray-300 font-medium">Momentum</h3>
              <p className={`text-xl font-bold ${getColor(data.momentum)}`}>
                {data.momentum || "–"}
              </p>
            </div>
            <div className="bg-gray-700 rounded-lg p-4 text-center space-y-1">
              <h3 className="text-sm text-gray-300 font-medium">The System</h3>
              <p className="text-sm">
                30m:{" "}
                <span className={`font-bold ${getColor(data.system_30m)}`}>
                  {data.system_30m || "–"}
                </span>
              </p>
              <p className="text-sm">
                1h:{" "}
                <span className={`font-bold ${getColor(data.system_1h)}`}>
                  {data.system_1h || "–"}
                </span>
              </p>
            </div>
          </div>

          {/* Row 2 */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm text-white">
            <div className="bg-gray-700 rounded-lg p-4 space-y-1">
              <p className="text-green-400 font-semibold mt-2">Premarket High</p>
              <p>{formatNum(data.premarket_high)}</p>
              <p className="text-red-300 font-semibold mt-2">Premarket Low</p>
              <p>{formatNum(data.premarket_low)}</p>
            </div>
            <div className="bg-gray-700 rounded-lg p-4 space-y-1">
              <p className="text-green-400 font-semibold">Prev Day High</p>
              <p>{formatNum(data.prev_day_high)}</p>
              <p className="text-red-300 font-semibold mt-2">Prev Day Low</p>
              <p>{formatNum(data.prev_day_low)}</p>
            </div>
            <div className="bg-gray-700 rounded-lg p-4 space-y-1">
              <p className="text-white font-semibold">Prev Close</p>
              <p>{formatNum(data.prev_day_close)}</p>
            </div>
            <div className="bg-gray-700 rounded-lg p-4 space-y-1">
              <p className="text-white font-semibold">Current Price</p>
              <p>{formatNum(data.current_price)}</p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
