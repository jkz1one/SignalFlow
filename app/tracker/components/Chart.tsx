'use client';

import { useRef } from 'react';
import { useCandlestickChart } from './chart/useCandlestickChart';
import CrosshairTooltip from './chart/CrosshairTooltip';

interface Candle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
}

interface ChartProps {
  candles?: Candle[];
  symbol?: string;
}

export default function Chart({ candles = [], symbol = 'SPY' }: ChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const { hasData, crosshairTime, crosshairX, resetView } = useCandlestickChart(candles, symbol, containerRef);

  const showChart = candles.length > 0;

  return (
    <div className="w-full relative">
      {/* Title */}
      <div className="text-sm text-gray-300 mb-1">{symbol} Chart</div>

      {/* Chart Container with overlayed button */}
      <div className="relative w-full h-[300px] bg-gray-800 rounded-md">
        {showChart && hasData && (
          <button
            onClick={resetView}
            className="absolute top-2 left-2 text-lg px-2 py-1 rounded bg-gray-800 text-gray-300 hover:bg-gray-700 z-10"
            title="Reset View"
          >
            ↻
          </button>
        )}

        {showChart && crosshairTime && crosshairX !== null && (
          <CrosshairTooltip time={crosshairTime} x={crosshairX} />
        )}

        <div ref={containerRef} className="absolute inset-0" />
      </div>

      {!showChart && (
        <div className="text-gray-400 text-center text-sm pt-2">
          No chart data available.
        </div>
      )}
    </div>
  );
}

