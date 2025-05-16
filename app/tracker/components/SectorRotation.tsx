'use client';

import { useEffect, useState } from 'react';

interface SectorData {
  sector: string;               // ETF symbol like XLF
  changePercent: number;        // always defined, skip malformed entries
  fullName?: string;            // full sector name
}

const SECTOR_NAME_MAP: Record<string, string> = {
  XLF: 'Financials',
  XLK: 'Technology',
  XLE: 'Energy',
  XLV: 'Healthcare',
  XLY: 'Consumer Discretionary',
  XLI: 'Industrials',
  XLP: 'Consumer Staples',
  XLU: 'Utilities',
  XLRE: 'Real Estate',
  XLB: 'Materials',
  XLC: 'Communication Services',
};

export default function SectorRotation() {
  const [sectors, setSectors] = useState<SectorData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchSectors() {
      try {
        const res = await fetch('/api/sector');
        const json = await res.json();

        if (!json || typeof json !== 'object' || Object.keys(json).length === 0) {
          // API blank or completely missing
          setSectors([]);
        } else {
          // Skip malformed or missing entries
          const parsed = Object.entries(json)
            .filter(([, data]: [string, any]) => data && Number.isFinite(data.pct_change))
            .map(([symbol, data]: [string, any]) => ({
              sector: symbol,
              changePercent: data.pct_change as number,
              fullName: SECTOR_NAME_MAP[symbol] || '',
            }));
          setSectors(parsed);
        }
      } catch (err) {
        console.error('Failed to fetch sector data', err);
        // On error, treat as no data
        setSectors([]);
      } finally {
        setLoading(false);
      }
    }

    fetchSectors();
  }, []);

  if (loading) {
    return <div className="text-gray-400 text-sm">Loading sector data...</div>;
  }

  if (sectors.length === 0) {
    return <div className="text-gray-400 text-sm">No sector data available.</div>;
  }

  return (
    <div className="space-y-4">
      {sectors.map((sector) => (
        <div
          key={sector.sector}
          className="bg-gray-800 rounded-lg shadow-md px-4 py-3"
        >
          <div className="flex justify-between items-center">
            <div className="text-xl font-bold text-gray-100">
              {sector.sector}
              {sector.fullName && (
                <span className="text-gray-400 text-sm"> ({sector.fullName})</span>
              )}
            </div>
            <div
              className={`text-lg font-semibold ${
                sector.changePercent >= 0 ? 'text-green-400' : 'text-red-400'
              }`}
            >
              {`${sector.changePercent >= 0 ? '+' : ''}${sector.changePercent.toFixed(2)}%`}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

