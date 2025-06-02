'use client';

import { useEffect, useState } from 'react';

interface SectorData {
  symbol: string;      // ETF ticker, e.g., XLF
  fullName: string;    // full sector name from API
  price: number;       // current price from API
  changePercent: number; // percent change value
}

export default function SectorRotation() {
  const [sectors, setSectors] = useState<SectorData[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [secondsSince, setSecondsSince] = useState<number>(0);
  const [sortDescending, setSortDescending] = useState(true); // true: gainers→losers

  // Fetch & poll data
  useEffect(() => {
    async function fetchSectors() {
      try {
        const res = await fetch('/api/sector');
        const json = await res.json();
        const raw = json.data && typeof json.data === 'object' ? json.data : {};

        const parsed: SectorData[] = Object.entries(raw)
          .filter(([, entry]: [string, any]) =>
            entry && typeof entry.changePercent === 'number' && typeof entry.price === 'number'
          )
          .map(([symbol, entry]: [string, any]) => ({
            symbol,
            fullName: entry.sector || '',
            price: entry.price,
            changePercent: entry.changePercent,
          }));

        setSectors(parsed);
        setLastUpdated(new Date());
      } catch (err) {
        console.error('Failed to fetch sector data', err);
        setSectors([]);
      } finally {
        setLoading(false);
      }
    }

    fetchSectors();
    const interval = setInterval(fetchSectors, 30000);
    return () => clearInterval(interval);
  }, []);

  // Live timer
  useEffect(() => {
    if (!lastUpdated) return;
    setSecondsSince(Math.floor((Date.now() - lastUpdated.getTime()) / 1000));
    const timer = setInterval(() => {
      setSecondsSince(Math.floor((Date.now() - lastUpdated.getTime()) / 1000));
    }, 1000);
    return () => clearInterval(timer);
  }, [lastUpdated]);

  if (loading) {
    return <div className="text-gray-400 text-sm">Loading sector data...</div>;
  }

  if (sectors.length === 0) {
    return <div className="text-gray-400 text-sm">No sector data available.</div>;
  }

  // Sort based on toggle
  const sorted = [...sectors].sort((a, b) =>
    sortDescending
      ? b.changePercent - a.changePercent
      : a.changePercent - b.changePercent
  );

  return (
    <div className="space-y-4 w-full">
      {/* Toggle button */}
      <div className="flex justify-end w-full pr-4">
        <select
          value={sortDescending ? 'desc' : 'asc'}
          onChange={e => setSortDescending(e.target.value === 'desc')}
          className="bg-gray-700 text-gray-200 text-sm px-3 py-1 rounded w-[160px] text-center"
        >
          <option value="desc">Gainers → Losers</option>
          <option value="asc">Losers → Gainers</option>
        </select>
      </div>



      {sorted.map((sector) => {
        const colorClass = sector.changePercent >= 0 ? 'text-green-400' : 'text-red-400';
        return (
          <div
            key={sector.symbol}
            className="bg-gray-800 rounded-lg shadow-md px-4 py-3"
          >
            <div className="flex justify-between items-center">
              <div className="text-xl font-bold text-gray-100">
                {sector.symbol}
                {sector.fullName && (
                  <span className="text-gray-400 text-sm"> {sector.fullName}</span>
                )}
              </div>
              <div className="flex items-baseline gap-2 text-right">
                <div className="text-lg font-semibold text-gray-400">
                  ${sector.price.toFixed(2)}
                </div>
                <div className={`text-xl font-bold ${colorClass}`}>
                  {`${sector.changePercent >= 0 ? '+' : ''}${sector.changePercent.toFixed(2)}%`}
                </div>
              </div>

            </div>
          </div>
        );
      })}

      <div className="flex w-full justify-end text-gray-400 text-xs">
        Updated at {lastUpdated?.toLocaleTimeString()} ({secondsSince}s ago)
      </div>
    </div>
  );
}
