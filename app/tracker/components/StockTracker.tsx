// Updated StockTracker.tsx with smart cache_only routing

'use client';

import { useEffect, useState, FormEvent, ChangeEvent, useRef } from 'react';
import Chart from './Chart';

// ...types remain unchanged

type TrackerData = {
  timestamp?: string;
  momentum?: string;
  system_30m?: string;
  system_1h?: string;
  premarket_high?: number | null;
  premarket_low?: number | null;
  daily_high?: number | null;
  daily_low?: number | null;
  prev_day_high?: number | null;
  prev_day_low?: number | null;
  current_price?: number | null;
};

interface Candle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
}

const INTERVAL_OPTIONS = ['5m', '10m', '30m', '1h', '4h', '1d'];

export default function StockTracker() {
  const [symbol, setSymbol] = useState(() =>
    typeof window !== 'undefined' ? localStorage.getItem('symbol_tracker') || 'SPY' : 'SPY'
  );
  const [input, setInput] = useState(symbol);
  const [interval, setIntervalStr] = useState('5m');
  const [data, setData] = useState<TrackerData | null>(null);
  const [candles, setCandles] = useState<Candle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const latestSymbol = useRef(symbol);
  const latestInterval = useRef(interval);

  const formatNum = (val?: number | null): string =>
    val != null ? val.toFixed(2) : '–';

  const getColor = (val?: string): string => {
    if (val === 'Bullish') return 'text-green-400';
    if (val === 'Bearish') return 'text-red-400';
    if (val === 'Chop' || val === 'Neutral') return 'text-yellow-300';
    return 'text-white';
  };

  const fetchTracker = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/tracker/${latestSymbol.current}`);
      if (!res.ok) throw new Error('Failed to fetch tracker data');
      const json: TrackerData = await res.json();
      setData(json);
      localStorage.setItem('symbol_tracker', latestSymbol.current);
    } catch {
      setError('Error loading data');
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchCandles = async (force: boolean = false) => {
    try {
      const url = `/api/tracker-candles?symbol=${latestSymbol.current}&interval=${latestInterval.current}&cache_only=${!force}`;
      const res = await fetch(url);
      const json = await res.json();
      setCandles(json.candles || []);
    } catch {
      console.error('❌ Error fetching candles');
    }
  };

  useEffect(() => {
    fetchTracker();
    fetchCandles(true); // initial full fetch
    const id = setInterval(() => {
      fetchTracker();
      fetchCandles(true); // refresh every 60s
    }, 60000);
    return () => clearInterval(id);
  }, []);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const newSymbol = input.trim().toUpperCase();
    if (!newSymbol) return;
    setSymbol(newSymbol);
    latestSymbol.current = newSymbol;
    await Promise.all([
      fetchTracker(),
      fetchCandles(true),
    ]);
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setInput(e.target.value.toUpperCase());
  };

  const handleIntervalChange = (e: ChangeEvent<HTMLSelectElement>) => {
    const newInterval = e.target.value;
    setIntervalStr(newInterval);
    latestInterval.current = newInterval;
    fetchCandles(false); // cache-only fetch
  };

  return (
    <div className="bg-gray-800 p-4 rounded-2xl w-full max-w-6xl mx-auto space-y-4 shadow-lg">
      <form onSubmit={handleSubmit} className="flex flex-wrap items-center gap-2">
        <input
          className="bg-gray-700 text-white px-3 py-2 rounded-md w-32 border border-gray-600"
          value={input}
          onChange={handleInputChange}
          placeholder="Enter ticker"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-gray-700 text-white px-3 py-2 border border-gray-600 rounded-md w-32 disabled:opacity-50"
        >
          {loading ? 'Loading...' : input === symbol ? 'Refresh' : 'Search'}
        </button>
        <select
          value={interval}
          onChange={handleIntervalChange}
          className="bg-gray-700 text-white px-2 py-2 rounded-md border border-gray-600"
        >
          {INTERVAL_OPTIONS.map((opt) => (
            <option key={opt} value={opt}>{opt}</option>
          ))}
        </select>
      </form>

      {error && <p className="text-red-400">{error}</p>}

      {data && (
        <>
          <div className="text-right text-xs text-gray-400">
            Updated: {data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : '–'}
          </div>

          <div className="flex flex-wrap gap-3">
            <div className="bg-gray-700 rounded-lg p-4 text-center min-w-[300px] flex-1">
              <h3 className="text-xl text-gray-300 font-bold">Momentum</h3>
              <p className={`text-xl font-bold ${getColor(data.momentum)}`}>{data.momentum || '–'}</p>
            </div>
            <div className="bg-gray-700 rounded-lg p-4 text-center space-y-1 min-w-[300px] flex-1">
              <h3 className="text-xl text-gray-300 font-bold">The System</h3>
              <p>30m: <span className={`font-bold ${getColor(data.system_30m)}`}>{data.system_30m || '–'}</span></p>
              <p>1h: <span className={`font-bold ${getColor(data.system_1h)}`}>{data.system_1h || '–'}</span></p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm text-white">
            <div className="bg-gray-700 rounded-lg p-4 space-y-1">
              <p className="text-green-400 font-semibold">Premarket High</p>
              <p>{formatNum(data.premarket_high)}</p>
              <p className="text-red-300 font-semibold mt-2">Premarket Low</p>
              <p>{formatNum(data.premarket_low)}</p>
            </div>
            <div className="bg-gray-700 rounded-lg p-4 space-y-1">
              <p className="text-green-400 font-semibold">Daily High</p>
              <p>{formatNum(data.daily_high)}</p>
              <p className="text-red-300 font-semibold mt-2">Daily Low</p>
              <p>{formatNum(data.daily_low)}</p>
            </div>
            <div className="bg-gray-700 rounded-lg p-4 space-y-1">
              <p className="text-green-400 font-semibold">Previous Day High</p>
              <p>{formatNum(data.prev_day_high)}</p>
              <p className="text-red-300 font-semibold mt-2">Previous Day Low</p>
              <p>{formatNum(data.prev_day_low)}</p>
            </div>
            <div className="bg-gray-700 rounded-lg p-4 space-y-1">
              <p className="text-white font-semibold">Current Price</p>
              <p>{formatNum(data.current_price)}</p>
            </div>
          </div>

          {candles.length > 0 && (
            <div className="pt-6">
              <Chart candles={candles} symbol={symbol} />
            </div>
          )}
        </>
      )}
    </div>
  );
}
