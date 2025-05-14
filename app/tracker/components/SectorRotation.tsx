'use client';

import { useEffect, useState } from 'react';

interface SectorData {
  sector: string; // ETF symbol like XLF
  changePercent: number;
  fullName?: string;
  leaders?: string[];
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

        const parsed = Object.entries(json).map(([sector, data]: [string, any]) => ({
          sector,
          changePercent: data.pct_change,
          fullName: SECTOR_NAME_MAP[sector] || sector,
        }));

        setSectors(parsed);
      } catch (err) {
        console.error('Failed to fetch sector data', err);
      } finally {
        setLoading(false);
      }
    }

    fetchSectors();
  }, []);

  if (loading) {
    return <div className="text-gray-400 text-sm">Loading sector data...</div>;
  }

  if (!sectors.length) {
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
              {sector.sector} <span className="text-gray-400 text-sm">({sector.fullName})</span>
            </div>
            <div
              className={`text-lg font-semibold ${
                sector.changePercent >= 0
                  ? 'text-green-400'
                  : 'text-red-400'
              }`}
            >
              {sector.changePercent >= 0 ? '+' : ''}
              {sector.changePercent.toFixed(2)}%
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
