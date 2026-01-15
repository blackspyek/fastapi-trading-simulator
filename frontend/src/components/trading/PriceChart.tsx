import { useEffect, useRef, useMemo } from "react";
import { createChart, CandlestickSeries } from "lightweight-charts";
import type { IChartApi, Time } from "lightweight-charts";
import type { Kline } from "../../types/asset";

interface PriceChartProps {
  klines: Kline[];
  interval: string;
  onIntervalChange: (interval: string) => void;
}

const INTERVALS = [
  { value: "1m", label: "1m" },
  { value: "5m", label: "5m" },
  { value: "15m", label: "15m" },
  { value: "1h", label: "1H" },
  { value: "4h", label: "4H" },
  { value: "1d", label: "1D" },
];

export function PriceChart({
  klines,
  interval,
  onIntervalChange,
}: PriceChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  const chartData = useMemo(() => {
    return klines.map((k) => ({
      time: k.time as Time,
      open: k.open,
      high: k.high,
      low: k.low,
      close: k.close,
    }));
  }, [klines]);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: "transparent" },
        textColor: "#9ca3af",
      },
      grid: {
        vertLines: { color: "rgba(42, 46, 57, 0.5)" },
        horzLines: { color: "rgba(42, 46, 57, 0.5)" },
      },
      width: chartContainerRef.current.clientWidth,
      height: 400,
      crosshair: {
        mode: 1,
      },
      timeScale: {
        borderColor: "rgba(42, 46, 57, 0.8)",
        timeVisible: true,
      },
      rightPriceScale: {
        borderColor: "rgba(42, 46, 57, 0.8)",
      },
    });

    chartRef.current = chart;

    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#00d26a",
      downColor: "#ff3b5c",
      borderUpColor: "#00d26a",
      borderDownColor: "#ff3b5c",
      wickUpColor: "#00d26a",
      wickDownColor: "#ff3b5c",
      priceFormat: {
        type: "price",
        precision: 3,
        minMove: 0.001,
      },
    });

    if (chartData.length > 0) {
      candlestickSeries.setData(chartData);
      chart.timeScale().fitContent();
    }

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [chartData]);

  return (
    <div className="bg-navy-900/50 border border-navy-700 rounded-2xl overflow-hidden">
      <div className="px-4 py-3 border-b border-navy-700 flex items-center justify-between">
        <h3 className="text-white font-semibold">Wykres cenowy</h3>
        <div className="flex gap-1">
          {INTERVALS.map((int) => (
            <button
              key={int.value}
              onClick={() => onIntervalChange(int.value)}
              className={`
                px-3 py-1 text-sm rounded-lg transition-colors cursor-pointer
                ${
                  interval === int.value
                    ? "bg-trading-cyan text-navy-950 font-medium"
                    : "text-gray-400 hover:text-white hover:bg-navy-800"
                }
              `}
            >
              {int.label}
            </button>
          ))}
        </div>
      </div>
      <div ref={chartContainerRef} className="w-full" />
    </div>
  );
}
