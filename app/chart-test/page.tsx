// app/chart-test/page.tsx

'use client';

import { useEffect, useState } from 'react';
import Chart from '../tracker/components/Chart';

interface Candle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
}

export default function ChartTest() {
  const [candles, setCandles] = useState<Candle[]>([]);
  const [loading, setLoading] = useState(true);
  const symbol = 'SPY';
  const interval = '5m';

  useEffect(() => {
    fetch(`/api/tracker-candles?symbol=${symbol}&interval=${interval}`)
      .then((res) => res.json())
      .then((data) => {
        setCandles(data.candles || []);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, [symbol, interval]);

  if (loading) {
    return <div className="text-white">Loading candles...</div>;
  }

  return (
    <div className="p-4 bg-gray-800 min-h-screen">
      <h2 className="text-green-400 text-xl mb-2">
        Chart Test: {symbol} {interval}
      </h2>
      <Chart candles={candles} symbol={symbol} />
    </div>
  );
}
