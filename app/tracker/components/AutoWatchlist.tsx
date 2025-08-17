'use client';

import { useEffect, useState } from 'react';
import WatchlistControls from './WatchlistControls';

type Tier = 'T1' | 'T2' | 'T3';

type Screener = {
  name: string;
  tier: Tier;
  tooltip: string;
};

type Stock = {
  symbol: string;
  score: number;
  tags: string[];
  screeners: Screener[];
  isBlocked: boolean;
  reasons: string[];
};

type SystemStatus = {
  scraping: boolean;
  phase: 'running' | 'idle' | 'completed' | 'error' | null;
  process?: string | null;
  watchlist_count?: number;
};

// Shape of /api/autowatchlist response: { [symbol]: { ...fields... } }
type WatchlistEntry = {
  score: number;
  tags?: string[];
  screeners?: Screener[];
  isBlocked?: boolean;
  reasons?: string[];
};
type WatchlistResponse = Record<string, WatchlistEntry>;

export default function AutoWatchlist() {
  const [data, setData] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string[]>([]);
  const [tiersShown, setTiersShown] = useState<Record<Tier, boolean>>({
    T1: true,
    T2: true,
    T3: true,
  });
  const [showRisk, setShowRisk] = useState(true);
  const [tagFilters, setTagFilters] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState<'score' | 'symbol'>('score');
  const [status, setStatus] = useState<SystemStatus | null>(null);

  function formatLabel(text: string) {
    return text.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
  }

  // Fetch watchlist once on load
  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch('/api/autowatchlist');
        const json = (await res.json()) as WatchlistResponse;

        const mapped: Stock[] = Object.entries(json).map(([symbol, stock]) => ({
          symbol,
          score: stock.score ?? 0,
          tags: stock.tags ?? [],
          isBlocked: stock.isBlocked ?? false,
          reasons: stock.reasons ?? [],
          screeners: (stock.screeners ?? []).filter(
            (s): s is Screener =>
              !!s &&
              typeof s.name === 'string' &&
              (s.tier === 'T1' || s.tier === 'T2' || s.tier === 'T3') &&
              typeof s.tooltip === 'string'
          ),
        }));

        setData(mapped);
      } catch (err) {
        console.error('Failed to fetch autowatchlist', err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  // Poll read-only system status every 15s
  useEffect(() => {
    let alive = true;

    const loadStatus = async () => {
      try {
        const res = await fetch('/api/system-status');
        const j = (await res.json()) as SystemStatus;
        if (alive) setStatus(j);
      } catch {
        // soft-fail: leave status as-is
      }
    };

    loadStatus();
    const id = setInterval(loadStatus, 15000);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);

  const toggleRow = (symbol: string, isCmdOrCtrl: boolean) => {
    setExpanded((prev) => {
      const isOpen = prev.includes(symbol);
      return isCmdOrCtrl
        ? isOpen
          ? prev.filter((s) => s !== symbol)
          : [...prev, symbol]
        : isOpen
        ? []
        : [symbol];
    });
  };

  const filtered = data
    .filter((stock) => {
      const grouped = { T1: [] as Screener[], T2: [] as Screener[], T3: [] as Screener[] };
      stock.screeners.forEach((s) => grouped[s.tier].push(s));
      const matchesTier =
        (tiersShown.T1 && grouped.T1.length > 0) ||
        (tiersShown.T2 && grouped.T2.length > 0) ||
        (tiersShown.T3 && grouped.T3.length > 0);

      const riskDisqualified = stock.isBlocked;
      const matchesTags =
        tagFilters.length === 0 || tagFilters.some((tag) => stock.tags.includes(tag));

      return matchesTier && matchesTags && (showRisk || !riskDisqualified);
    })
    .sort((a, b) => (sortBy === 'score' ? b.score - a.score : a.symbol.localeCompare(b.symbol)));

  if (loading) {
    return <div className="text-gray-400 text-sm">Loading watchlist...</div>;
  }

  return (
    <div className="space-y-4">
      <WatchlistControls
        tiersShown={tiersShown}
        setTiersShown={setTiersShown}
        showRisk={showRisk}
        setShowRisk={setShowRisk}
        tagFilters={tagFilters}
        setTagFilters={setTagFilters}
        sortBy={sortBy}
        setSortBy={(val) => (val === 'score' || val === 'symbol' ? setSortBy(val) : null)}
      />

      {/* Status message under filter row (read-only) */}
      {status && (
        <div className="flex justify-center">
          <div className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-lg text-gray-300 font-bold">
            {status.scraping
              ? '🚀 Building Signals…'
              : filtered.length === 0
              ? '⏳ No Candidates – System Idle '
              : null}
          </div>
        </div>
      )}

      {filtered.map((stock) => {
        const isOpen = expanded.includes(stock.symbol);
        const groupedScreeners: Record<Tier, Screener[]> = { T1: [], T2: [], T3: [] };
        stock.screeners.forEach((s) => groupedScreeners[s.tier].push(s));

        return (
          <div key={stock.symbol} className="bg-gray-800 rounded-lg shadow-md">
            <div
              className="flex justify-between items-center px-4 py-3 cursor-pointer"
              onClick={(e) => toggleRow(stock.symbol, e.metaKey || e.ctrlKey)}
            >
              <div className="flex items-center gap-4 flex-wrap">
                <div className="text-lg font-bold">{stock.symbol}</div>
                <div className="text-sm text-gray-400">Score: {stock.score}</div>
                {stock.tags.map((tag) => (
                  <span
                    key={tag}
                    className="bg-gray-700 text-xs px-2 py-0.5 rounded-full text-gray-200"
                  >
                    {tag}
                  </span>
                ))}

                {((['T1', 'T2', 'T3'] as const) as Tier[]).map((tier) =>
                  tiersShown[tier] && groupedScreeners[tier].length > 0 ? (
                    <span
                      key={`${stock.symbol}-${tier}`}
                      title={groupedScreeners[tier].map((s) => `✓ ${s.tooltip}`).join('\n')}
                      className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                        tier === 'T1'
                          ? 'bg-green-600 text-white'
                          : tier === 'T2'
                          ? 'bg-blue-500 text-white'
                          : 'bg-purple-600 text-white'
                      }`}
                    >
                      {tier}
                    </span>
                  ) : null
                )}
              </div>
              <div className="text-gray-400 text-sm">{isOpen ? '▲' : '▼'}</div>
            </div>

            {isOpen && (
              <div className="grid grid-cols-3 gap-4 bg-gray-700 px-4 py-3 text-sm text-gray-200 border-t border-gray-600">
                {((['T1', 'T2', 'T3'] as const) as Tier[]).map(
                  (tier) =>
                    groupedScreeners[tier].length > 0 && (
                      <div key={`${stock.symbol}-col-${tier}`}>
                        <h4
                          className={`font-bold mb-1 ${
                            tier === 'T1'
                              ? 'text-green-400'
                              : tier === 'T2'
                              ? 'text-blue-400'
                              : 'text-purple-400'
                          }`}
                        >
                          Tier {tier[1]}
                        </h4>
                        <ul className="space-y-1">
                          {groupedScreeners[tier].map((s) => (
                            <li key={s.name}>
                              ✓ {formatLabel(s.name)}
                              {s.tooltip && /\d/.test(s.tooltip) && (
                                <span className="ml-[0.9rem] text-gray-500 italic font-light">
                                  {s.tooltip}
                                </span>
                              )}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )
                )}

                {stock.reasons.length > 0 && (
                  <div className="col-span-3 pt-2 border-t border-gray-600">
                    <h4 className="text-red-400 font-semibold text-sm mb-1">Risk Flags</h4>
                    <ul className="flex gap-3 text-xs text-red-300">
                      {stock.reasons.map((flag) => (
                        <li key={flag}>⚠ {formatLabel(flag)}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="col-span-3 flex justify-end">
                  <button
                    onClick={() => (window.location.href = `/tracker?ticker=${stock.symbol}`)}
                    className="text-green-400 hover:text-green-300 text-xs font-medium"
                  >
                    Tracker →
                  </button>
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
