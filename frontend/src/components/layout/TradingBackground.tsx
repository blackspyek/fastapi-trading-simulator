import { useEffect, useState } from "react";

interface Candle {
  id: number;
  left: string;
  height: string;
  delay: string;
  duration: string;
  color: "green" | "red";
}

export function TradingBackground() {
  const [candles, setCandles] = useState<Candle[]>([]);

  useEffect(() => {
    const newCandles: Candle[] = Array.from({ length: 15 }).map((_, i) => ({
      id: i,
      left: `${Math.random() * 100}%`,
      height: `${Math.random() * 20 + 10}%`, // 10-30% height
      delay: `${Math.random() * 2}s`,
      duration: `${Math.random() * 2 + 2}s`, // 2-4s duration
      color: Math.random() > 0.5 ? "green" : "red",
    }));
    setCandles(newCandles);
  }, []);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none bg-navy-950">
      <div
        className="absolute inset-0 opacity-10"
        style={{
          backgroundImage: `
            linear-gradient(rgba(0, 212, 255, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 212, 255, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: "40px 40px",
        }}
      />

      <div className="absolute inset-0 bg-gradient-to-t from-navy-950 via-transparent to-navy-950/80" />
      <div className="absolute inset-0 bg-gradient-to-r from-navy-950 via-transparent to-navy-950/80" />
      <div className="absolute inset-0 flex flex-row justify-between opacity-20">
        {candles.map((candle) => (
          <div
            key={candle.id}
            className={`absolute bottom-0 w-8 md:w-12 rounded-t-sm transition-all animate-pulse ${
              candle.color === "green" ? "bg-trading-green" : "bg-trading-red"
            }`}
            style={{
              left: candle.left,
              height: candle.height,
              animationDelay: candle.delay,
              animationDuration: candle.duration,
              opacity: 0.3,
            }}
          >
            <div
              className={`absolute top-0 left-1/2 -translate-x-1/2 -translate-y-full w-0.5 h-8 ${
                candle.color === "green" ? "bg-trading-green" : "bg-trading-red"
              }`}
            />
          </div>
        ))}
      </div>

      <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-trading-cyan to-transparent opacity-50" />
      <div className="absolute bottom-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-trading-green to-transparent opacity-50" />
    </div>
  );
}
