'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import AutoWatchlist from './components/AutoWatchlist';
import SectorRotation from './components/SectorRotation';
import StockTracker from './components/StockTracker';
import GlobalContextBar from './components/GlobalContextBar';

const TABS = ['Auto-Watchlist', 'Stock Tracker', 'Sector Rotation'];

// Wrapper page component (no hooks)
export default function TrackerPage() {
  return (
    <Suspense fallback={<div className="text-gray-400 text-sm p-4">Loading…</div>}>
      <TrackerPageInner />
    </Suspense>
  );
}

// Inner client component that uses useSearchParams()
function TrackerPageInner() {
  const searchParams = useSearchParams();
  const tickerParam = searchParams.get('ticker');

  const [activeTab, setActiveTab] = useState('Auto-Watchlist');
  const [symbol, setSymbol] = useState('SPY');

  useEffect(() => {
    if (tickerParam) {
      const up = tickerParam.toUpperCase();
      setSymbol(up);
      setActiveTab('Stock Tracker');
      if (typeof window !== 'undefined') {
        localStorage.setItem('symbol_tracker', up);
      }
    }
  }, [tickerParam]);

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 p-4 space-y-4">
      <div className="flex justify-center gap-2">
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg font-semibold transition text-sm sm:text-base ${
              activeTab === tab
                ? 'bg-gray-700 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      <GlobalContextBar />

      <div className="mt-4">
        {activeTab === 'Auto-Watchlist' && <AutoWatchlist />}
        {activeTab === 'Stock Tracker' && <StockTracker symbol={symbol} />}
        {activeTab === 'Sector Rotation' && <SectorRotation />}
      </div>
    </div>
  );
}
