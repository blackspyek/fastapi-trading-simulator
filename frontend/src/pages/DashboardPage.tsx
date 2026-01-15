import { useEffect, useState, useCallback } from "react";
import { useAuth } from "../context/AuthContext";
import { useWebSocket } from "../hooks/useWebSocket";
import { getAssets, getAssetKlines } from "../api/assetsApi";
import { getWallet, buyAsset, sellAsset } from "../api/tradeApi";
import { CryptoSelector } from "../components/trading/CryptoSelector";
import { AssetInfo } from "../components/trading/AssetInfo";
import { PriceChart } from "../components/trading/PriceChart";
import { TradePanel } from "../components/trading/TradePanel";
import { WalletCard } from "../components/trading/WalletCard";
import type { AssetPrice, Kline, WalletStatus } from "../types/asset";

export function DashboardPage() {
  const { user, logout } = useAuth();
  const { prices: livePrices, isConnected, serverStatus } = useWebSocket();

  const [assets, setAssets] = useState<AssetPrice[]>([]);
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const [klines, setKlines] = useState<Kline[]>([]);
  const [interval, setInterval] = useState("1h");
  const [wallet, setWallet] = useState<WalletStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const selectedAsset = assets.find((a) => a.ticker === selectedTicker) ?? null;
  const walletAsset = wallet?.assets?.find((a) => a.ticker === selectedTicker);

  useEffect(() => {
    async function loadData() {
      try {
        const [assetsData, walletData] = await Promise.all([
          getAssets(),
          getWallet(),
        ]);
        setAssets(assetsData);
        setWallet(walletData);
        if (assetsData.length > 0 && !selectedTicker) {
          setSelectedTicker(assetsData[0].ticker);
        }
      } catch (err) {
        console.error("Error loading data:", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  useEffect(() => {
    async function loadKlines() {
      if (!selectedTicker) return;

      const asset = assets.find((a) => a.ticker === selectedTicker);
      if (!asset) return;

      try {
        const klinesData = await getAssetKlines(asset.id, interval, 100);
        setKlines(klinesData);
      } catch (err) {
        console.error("Error loading klines:", err);
        setKlines([]);
      }
    }
    loadKlines();
  }, [selectedTicker, interval, assets]);

  const refreshWallet = useCallback(async () => {
    try {
      const walletData = await getWallet();
      setWallet(walletData);
    } catch (err) {
      console.error("Error refreshing wallet:", err);
    }
  }, []);

  const handleBuy = async (ticker: string, amount: number) => {
    await buyAsset(ticker, amount);
    await refreshWallet();
  };

  const handleSell = async (ticker: string, amount: number) => {
    await sellAsset(ticker, amount);
    await refreshWallet();
  };

  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-navy-950">
      <header className="border-b border-navy-800 bg-navy-900/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-trading-cyan to-trading-green rounded-lg flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-navy-950"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                  />
                </svg>
              </div>
              <span className="text-lg font-bold text-white">
                TradingSimulator
              </span>
            </div>

            <div className="flex items-center gap-4">
              <div className="hidden sm:flex items-center gap-2 px-4 py-2 bg-navy-800/50 rounded-lg border border-navy-700 relative group cursor-default">
                <div
                  className={`w-2 h-2 rounded-full ${
                    isConnected
                      ? "bg-trading-green animate-pulse"
                      : "bg-trading-red"
                  }`}
                />
                <span className="text-gray-300 text-sm">
                  {isConnected ? "Connected" : "Offline"}
                </span>
                {isConnected && serverStatus && (
                  <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 px-3 py-2 bg-navy-800 border border-navy-600 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50 shadow-lg w-56">
                    <div className="text-xs text-gray-400 mb-1">Server Status</div>
                    <div className="flex gap-4 text-sm font-mono flex-nowrap">
                      <div className="whitespace-nowrap">
                        <span className="text-gray-400">CPU:</span>{" "}
                        <span className="text-trading-cyan font-medium">{serverStatus.cpu.toFixed(1).padStart(5)}%</span>
                      </div>
                      <div className="whitespace-nowrap">
                        <span className="text-gray-400">RAM:</span>{" "}
                        <span className="text-trading-cyan font-medium">{serverStatus.ram.toFixed(1).padStart(5)}%</span>
                      </div>
                    </div>
                    <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-navy-800 border-l border-t border-navy-600 rotate-45"></div>
                  </div>
                )}
              </div>
              <div className="text-right hidden sm:block">
                <div className="text-sm text-gray-400">Witaj</div>
                <div className="text-white font-medium">{user?.username}</div>
              </div>
              {user?.role === 'admin' && (
                <a
                  href="/admin"
                  className="px-4 py-2 bg-navy-800 text-trading-cyan border border-trading-cyan/30 rounded-lg text-sm font-medium hover:bg-navy-700 transition-colors"
                >
                  Panel Admina
                </a>
              )}
              <button
                onClick={logout}
                className="px-4 py-2 bg-trading-red/10 border border-trading-red/30 text-trading-red rounded-lg text-sm font-medium hover:bg-trading-red/20 transition-colors cursor-pointer"
              >
                Wyloguj
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-3">
            <CryptoSelector
              assets={assets}
              selectedTicker={selectedTicker}
              onSelect={setSelectedTicker}
              livePrices={livePrices}
            />
          </div>

          <div className="lg:col-span-6 space-y-6">
            <AssetInfo
              asset={selectedAsset}
              livePrice={
                selectedTicker ? livePrices[selectedTicker] : undefined
              }
            />
            <PriceChart
              klines={klines}
              interval={interval}
              onIntervalChange={setInterval}
            />
          </div>

          <div className="lg:col-span-3 space-y-6">
            <WalletCard wallet={wallet} livePrices={livePrices} onResetComplete={refreshWallet} />
            <TradePanel
              asset={selectedAsset}
              balance={wallet?.balance ?? 0}
              walletAsset={walletAsset}
              livePrice={
                selectedTicker ? livePrices[selectedTicker] : undefined
              }
              onBuy={handleBuy}
              onSell={handleSell}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
