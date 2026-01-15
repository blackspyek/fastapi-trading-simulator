import { useState } from "react";
import type { AssetPrice, WalletAsset } from "../../types/asset";

interface TradePanelProps {
  asset: AssetPrice | null;
  balance: number;
  walletAsset: WalletAsset | undefined;
  livePrice?: number;
  onBuy: (ticker: string, amount: number) => Promise<void>;
  onSell: (ticker: string, amount: number) => Promise<void>;
}

export function TradePanel({
  asset,
  balance,
  walletAsset,
  livePrice,
  onBuy,
  onSell,
}: TradePanelProps) {
  const [activeTab, setActiveTab] = useState<"buy" | "sell">("buy");
  const [amount, setAmount] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  if (!asset) {
    return (
      <div className="bg-navy-900/50 border border-navy-700 rounded-2xl p-6 text-center">
        <p className="text-gray-400">Wybierz kryptowalutę, aby handlować</p>
      </div>
    );
  }

  const price = livePrice ?? asset.current_price;
  const numAmount = parseFloat(amount) || 0;
  const totalCost = numAmount * price;
  const canBuy = totalCost > 0 && totalCost <= balance;
  const canSell =
    numAmount > 0 && walletAsset && numAmount <= walletAsset.amount;

  const handleSubmit = async () => {
    if (!amount || numAmount <= 0) return;

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      if (activeTab === "buy") {
        await onBuy(asset.ticker, numAmount);
        setSuccess(`Kupiono ${numAmount} ${asset.ticker}!`);
      } else {
        await onSell(asset.ticker, numAmount);
        setSuccess(`Sprzedano ${numAmount} ${asset.ticker}!`);
      }
      setAmount("");
    } catch (err: any) {
      setError(err.message || "Wystąpił błąd");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-navy-900/50 border border-navy-700 rounded-2xl overflow-hidden">
      <div className="flex border-b border-navy-700">
        <button
          onClick={() => {
            setActiveTab("buy");
            setError(null);
            setSuccess(null);
          }}
          className={`
            flex-1 py-3 font-semibold transition-colors cursor-pointer
            ${
              activeTab === "buy"
                ? "bg-trading-green/10 text-trading-green border-b-2 border-trading-green"
                : "text-gray-400 hover:text-white"
            }
          `}
        >
          Kup
        </button>
        <button
          onClick={() => {
            setActiveTab("sell");
            setError(null);
            setSuccess(null);
          }}
          className={`
            flex-1 py-3 font-semibold transition-colors cursor-pointer
            ${
              activeTab === "sell"
                ? "bg-trading-red/10 text-trading-red border-b-2 border-trading-red"
                : "text-gray-400 hover:text-white"
            }
          `}
        >
          Sprzedaj
        </button>
      </div>

      <div className="p-4 space-y-4">
        <div>
          <label className="block text-gray-400 text-sm mb-2">
            Ilość ({asset.ticker})
          </label>
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="0.00"
            min="0"
            step="0.0001"
            className="w-full px-4 py-3 bg-navy-800 border border-navy-600 rounded-xl text-white placeholder-gray-500 focus:border-trading-cyan"
          />
        </div>

        <div className="space-y-2 text-sm">
          <div className="flex justify-between text-gray-400">
            <span>Cena:</span>
            <span className="text-white">
              $
              {price.toLocaleString("en-US", {
                minimumFractionDigits: 3,
                maximumFractionDigits: 3,
              })}
            </span>
          </div>
          <div className="flex justify-between text-gray-400">
            <span>{activeTab === "buy" ? "Koszt:" : "Przychód:"}</span>
            <span className="text-white font-medium">
              $
              {totalCost.toLocaleString("en-US", {
                minimumFractionDigits: 3,
                maximumFractionDigits: 3,
              })}
            </span>
          </div>
          {activeTab === "buy" && (
            <div className="flex justify-between text-gray-400">
              <span>Dostępne saldo:</span>
              <span className="text-trading-cyan">
                $
                {balance.toLocaleString("en-US", {
                minimumFractionDigits: 3,
                  maximumFractionDigits: 3,
                })}
              </span>
            </div>
          )}
          {activeTab === "sell" && (
            <div className="flex justify-between text-gray-400">
              <span>Posiadasz:</span>
              <span className="text-trading-cyan">
                {walletAsset?.amount.toFixed(4) || "0"} {asset.ticker}
              </span>
            </div>
          )}
        </div>

        {error && (
          <div className="p-3 bg-trading-red/10 border border-trading-red/30 rounded-lg text-trading-red text-sm">
            {error}
          </div>
        )}
        {success && (
          <div className="p-3 bg-trading-green/10 border border-trading-green/30 rounded-lg text-trading-green text-sm">
            {success}
          </div>
        )}

        <button
          onClick={handleSubmit}
          disabled={isLoading || (activeTab === "buy" ? !canBuy : !canSell)}
          className={`
            w-full py-3 rounded-xl font-semibold transition-all cursor-pointer
            disabled:opacity-50 disabled:cursor-not-allowed
            ${
              activeTab === "buy"
                ? "bg-trading-green text-navy-950 hover:shadow-lg hover:shadow-trading-green/25"
                : "bg-trading-red text-white hover:shadow-lg hover:shadow-trading-red/25"
            }
          `}
        >
          {isLoading
            ? "Przetwarzanie..."
            : activeTab === "buy"
            ? `Kup ${asset.ticker}`
            : `Sprzedaj ${asset.ticker}`}
        </button>
      </div>
    </div>
  );
}
