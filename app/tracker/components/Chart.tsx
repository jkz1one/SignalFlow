'use client';

import { useEffect, useRef, useState } from 'react';
import {
  createChart,
  CrosshairMode,
  CandlestickSeriesOptions,
  CandlestickData,
  Time,
  IChartApi,
  ISeriesApi,
} from 'lightweight-charts';

interface Candle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
}

interface ChartProps {
  candles: Candle[];
  symbol?: string;
}

export default function Chart({ candles, symbol = 'SPY' }: ChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const prevSymbolRef = useRef<string | null>(null);
  const [hasData, setHasData] = useState(false);

  // ✅ Create chart once
  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 300,
      layout: {
        background: { color: '#1f2937' },
        textColor: '#d1d5db',
      },
      grid: {
        vertLines: { color: '#374151' },
        horzLines: { color: '#374151' },
      },
      crosshair: { mode: CrosshairMode.Normal },
      rightPriceScale: {
        borderColor: '#9ca3af',
        scaleMargins: { top: 0.1, bottom: 0.1 },
        visible: true,
      },
      timeScale: {
        borderColor: '#9ca3af',
        rightOffset: 0,
        shiftVisibleRangeOnNewBar: false,
        rightBarStaysOnScroll: false,
      },
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,
        vertTouchDrag: false,
      },
    });

    const opts: Partial<CandlestickSeriesOptions> = {
      upColor: '#10b981',
      downColor: '#ef4444',
      wickUpColor: '#10b981',
      wickDownColor: '#ef4444',
      borderVisible: false,
    };

    const series = chart.addCandlestickSeries(opts);

    chartRef.current = chart;
    seriesRef.current = series;

    const resizeObserver = new ResizeObserver(() => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth });
      }
    });

    resizeObserver.observe(containerRef.current);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
  }, []);

  // ✅ Update candles + reset autoscale on symbol change
  useEffect(() => {
    if (!seriesRef.current || !chartRef.current || !candles || candles.length === 0) {
      setHasData(false);
      return;
    }

    const formatted: CandlestickData[] = candles.map((c) => ({
      time: c.time as Time,
      open: c.open,
      high: c.high,
      low: c.low,
      close: c.close,
    }));

    seriesRef.current.setData(formatted);
    setHasData(true);

    if (prevSymbolRef.current !== symbol) {
      chartRef.current.timeScale().fitContent();
      chartRef.current.priceScale('right').applyOptions({ autoScale: true });
    }

    prevSymbolRef.current = symbol;
  }, [candles, symbol]);

  const handleReset = () => {
    chartRef.current?.timeScale().fitContent();
    chartRef.current?.priceScale('right').applyOptions({ autoScale: true });
  };

  return (
    <div className="w-full relative">
      {/* Title */}
      <div className="text-sm text-gray-300 mb-1">{symbol} Chart</div>

      {/* ↻ Reset button, top-right absolute */}
      {hasData && (
        <button
          onClick={handleReset}
          className="absolute top-1 right-1 text-lg px-2 py-1 rounded bg-gray-800 text-gray-300 hover:bg-gray-700 z-10"
          title="Reset View"
        >
          ↻
        </button>
      )}

      {/* Chart container */}
      <div
        ref={containerRef}
        className="w-full h-[300px] bg-gray-900 rounded-md"
      />

      {/* Empty state */}
      {(!candles || candles.length === 0) && (
        <div className="text-gray-400 text-center text-sm pt-2">
          No chart data available.
        </div>
      )}
    </div>
  );
}
