/**
 * Komponent informacji o aktywie.
 * Wyświetla nazwę, cenę i zmianę.
 */

import type { AssetPrice } from '../../types/asset';

interface AssetInfoProps {
  asset: AssetPrice | null;
  livePrice?: number;
}

export function AssetInfo({ asset, livePrice }: AssetInfoProps) {
  if (!asset) {
    return (
      <div className="bg-navy-900/50 border border-navy-700 rounded-2xl p-6 text-center">
        <p className="text-gray-400">Wybierz kryptowalutę z listy po lewej</p>
      </div>
    );
  }

  const price = livePrice ?? asset.current_price;

  return (
    <div className="bg-navy-900/50 border border-navy-700 rounded-2xl p-6">
      <div className="flex items-center gap-4 mb-4">
        <div className="w-14 h-14 rounded-full bg-gradient-to-br from-trading-cyan to-trading-green flex items-center justify-center">
          <span className="text-navy-950 font-bold text-lg">
            {asset.ticker.slice(0, 2)}
          </span>
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white">{asset.name}</h2>
          <p className="text-gray-400">{asset.ticker}/USD</p>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-4xl font-bold text-white">
          ${price.toLocaleString('en-US', {
            minimumFractionDigits: 3,
            maximumFractionDigits: 3,
          })}
        </span>
        <div className="flex items-center gap-1 px-2 py-1 bg-trading-green/10 rounded-lg">
          <div className="w-2 h-2 bg-trading-green rounded-full animate-pulse" />
          <span className="text-trading-green text-sm font-medium">Live</span>
        </div>
      </div>
    </div>
  );
}
