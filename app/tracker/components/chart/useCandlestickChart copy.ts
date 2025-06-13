import {
  createChart,
  CrosshairMode,
  IChartApi,
  ISeriesApi,
  MouseEventParams,
  CandlestickSeriesOptions,
  CandlestickData,
  Time,
} from 'lightweight-charts';
import { useEffect, useRef, useState } from 'react';
import { DateTime } from 'luxon';
import { formatCrosshairTime } from './formatters';

interface Candle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
}

export const useCandlestickChart = (
  candles: Candle[],
  symbol: string,
  containerRef: React.RefObject<HTMLDivElement | null>
) => {
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const prevSymbolRef = useRef<string | null>(null);
  const newDayTimestamps = useRef<Set<number>>(new Set());

  const [hasData, setHasData] = useState(false);
  const [crosshairTime, setCrosshairTime] = useState<string | null>(null);
  const [crosshairX, setCrosshairX] = useState<number | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 300,
      layout: { background: { color: '#1f2937' }, textColor: '#d1d5db' },
      grid: {
        vertLines: { color: '#374151' },
        horzLines: { color: '#374151' },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: { labelVisible: false },
        horzLine: { labelVisible: true },
      },
      rightPriceScale: {
        borderColor: '#9ca3af',
        scaleMargins: { top: 0.1, bottom: 0.1 },
        visible: true,
      },
      timeScale: {
        borderColor: '#9ca3af',
        timeVisible: true,
        tickMarkMaxCharacterLength: 10,
      },
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,
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

    chart.subscribeCrosshairMove((param: MouseEventParams) => {
      if (!param.point || typeof param.time !== 'number') {
        setCrosshairTime(null);
        setCrosshairX(null);
        return;
      }
      setCrosshairTime(formatCrosshairTime(param.time));
      setCrosshairX(param.point.x);
    });

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

  useEffect(() => {
    if (!seriesRef.current || !chartRef.current || !candles?.length) {
      setHasData(false);
      return;
    }

    const formatted: CandlestickData[] = candles.map((c) => {
      const dt = DateTime.fromSeconds(c.time, { zone: 'utc' }).setZone('America/New_York');
      return {
        time: Math.floor(dt.toSeconds()) as Time,
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
      };
    });

    seriesRef.current.setData(formatted);
    setHasData(true);

    if (prevSymbolRef.current !== symbol) {
      chartRef.current.timeScale().fitContent();
      chartRef.current.priceScale('right').applyOptions({ autoScale: true });
    }

    prevSymbolRef.current = symbol;
  }, [candles, symbol]);

  const resetView = () => {
    chartRef.current?.timeScale().fitContent();
    chartRef.current?.priceScale('right').applyOptions({ autoScale: true });
  };

  return { hasData, crosshairTime, crosshairX, resetView };
};
