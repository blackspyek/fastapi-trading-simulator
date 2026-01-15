import type { AssetPrice } from "../../types/asset";

interface CryptoSelectorProps {
  assets: AssetPrice[];
  selectedTicker: string | null;
  onSelect: (ticker: string) => void;
  livePrices: Record<string, number>;
}

export function CryptoSelector({
  assets,
  selectedTicker,
  onSelect,
  livePrices,
}: CryptoSelectorProps) {
  return (
    <div className="bg-navy-900/50 border border-navy-700 rounded-2xl overflow-hidden">
      <div className="px-4 py-3 border-b border-navy-700">
        <h3 className="text-white font-semibold">Kryptowaluty</h3>
      </div>
      <div className="max-h-[400px] overflow-y-auto">
        {assets.map((asset) => {
          const price = livePrices[asset.ticker] ?? asset.current_price;
          const isSelected = selectedTicker === asset.ticker;

          return (
            <button
              key={asset.ticker}
              onClick={() => onSelect(asset.ticker)}
              className={`
                w-full px-4 py-3 flex items-center justify-between
                transition-colors cursor-pointer
                ${
                  isSelected
                    ? "bg-trading-cyan/10 border-l-2 border-trading-cyan"
                    : "hover:bg-navy-800/50 border-l-2 border-transparent"
                }
              `}
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-trading-cyan to-trading-green flex items-center justify-center">
                  <span className="text-navy-950 font-bold text-sm">
                    {asset.ticker.slice(0, 2)}
                  </span>
                </div>
                <div className="text-left">
                  <div className="text-white font-medium">{asset.ticker}</div>
                  <div className="text-gray-400 text-sm">{asset.name}</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-white font-medium">
                  $
                  {price.toLocaleString("en-US", {
                    minimumFractionDigits: 3,
                    maximumFractionDigits: 3,
                  })}
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
