'use client';

import { useEffect, useState } from 'react';

type Stock = {
  symbol: string;
  score: number;
  tags: string[];
  tier1: string[];
  tier2: string[];
  tier3: string[];
};

export default function WatchlistPage() {
  const [data, setData] = useState<Stock[]>([]);

  useEffect(() => {
    fetch('/api/autowatchlist')
      .then((res) => res.json())
      .then((json) => {
        console.log('API response:', json);
        const parsed = Object.entries(json).map(([symbol, entry]) => ({
          symbol,
          score: entry.score,
          tags: entry.tags || [],
          tier1: entry.tierHits?.T1 || [],
          tier2: entry.tierHits?.T2 || [],
          tier3: entry.tierHits?.T3 || [],
        }));
        setData(parsed);
      });
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 p-6">
      <h1 className="text-2xl font-bold mb-6">Auto-Watchlist</h1>
      {data.length === 0 ? (
        <p>No tickers found.</p>
      ) : (
        data.map((stock, idx) => (
          <div key={stock.symbol || `stock-${idx}`} className="mb-4 p-4 bg-gray-800 rounded shadow">
            <div className="text-xl font-bold text-white mb-1">{stock.symbol || '—'}</div>
            <div className="text-sm text-gray-300">Score: {stock.score}</div>
            <div className="text-sm text-blue-300 mb-1">Tags: {stock.tags?.join(', ') || '—'}</div>
            <div className="ml-2 space-y-1">
              {stock.tier1?.length > 0 && (
                <div><span className="text-green-400 font-semibold">T1:</span> {stock.tier1.join(', ')}</div>
              )}
              {stock.tier2?.length > 0 && (
                <div><span className="text-blue-300 font-semibold">T2:</span> {stock.tier2.join(', ')}</div>
              )}
              {stock.tier3?.length > 0 && (
                <div><span className="text-purple-400 font-semibold">T3:</span> {stock.tier3.join(', ')}</div>
              )}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
