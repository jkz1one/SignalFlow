'use client';

import { useState } from 'react';
import AutoWatchlist from './components/AutoWatchlist';
import SectorRotation from './components/SectorRotation';
import StockTracker from './components/StockTracker';  // ✅ Add this
import GlobalContextBar from './components/GlobalContextBar';

const TABS = ['Auto-Watchlist', 'Stock Tracker', 'Sector Rotation'];

export default function TrackerPage() {
  const [activeTab, setActiveTab] = useState('Auto-Watchlist');

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 p-4 space-y-4">
      {/* Tab Switcher */}
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

      {/* Global Context Bar directly under tab switcher */}
      <GlobalContextBar />

      {/* View Renderer */}
      <div className="mt-4">
        {activeTab === 'Auto-Watchlist' && <AutoWatchlist />}
        {activeTab === 'Stock Tracker' && <StockTracker />}
        {activeTab === 'Sector Rotation' && <SectorRotation />}
      </div>
    </div>
  );
}
