// app/tracker/components/chart/DateOverlay.tsx

'use client';

import { useEffect, useRef } from 'react';
import { IChartApi, Time } from 'lightweight-charts';

interface Candle {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
}

interface Props {
  chart: IChartApi | null;
  candles: Candle[];
}

export default function DateOverlay({ chart, candles }: Props) {
  const overlayRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chart || !overlayRef.current) return;

    const container = overlayRef.current;
    container.innerHTML = '';

    const seen = new Set<string>();

    candles.forEach(candle => {
      const date = new Date(candle.time * 1000);
      const dateStr = date.toDateString();
      if (seen.has(dateStr)) return;
      seen.add(dateStr);

      const x = chart.timeScale().timeToCoordinate(candle.time as Time);
      if (x === null) return;

      const el = document.createElement('div');
      el.className = 'absolute text-gray-400 text-[11px]';
      el.style.left = `${x}px`;
      el.style.transform = 'translateX(-50%)';
      el.textContent = date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      });

      container.appendChild(el);
    });
  }, [chart, candles]);

  return (
    <div
      ref={overlayRef}
      className="absolute left-0 right-0 h-5 bottom-[-18px] pointer-events-none z-10"
    />
  );
}
