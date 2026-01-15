import { useState } from "react";
import type { WalletStatus } from "../../types/asset";
import { resetAccount } from "../../api/tradeApi";

interface WalletCardProps {
  wallet: WalletStatus | null;
  livePrices: Record<string, number>;
  onResetComplete?: () => void;
}

export function WalletCard({ wallet, livePrices, onResetComplete }: WalletCardProps) {
  const [showResetDialog, setShowResetDialog] = useState(false);
  const [isResetting, setIsResetting] = useState(false);

  const handleResetAccount = async () => {
    setIsResetting(true);
    try {
      await resetAccount();
      setShowResetDialog(false);
      onResetComplete?.();
    } catch (error) {
      console.error("Błąd podczas resetowania konta:", error);
      alert("Nie udało się zresetować konta. Spróbuj ponownie.");
    } finally {
      setIsResetting(false);
    }
  };

  if (!wallet) {
    return (
      <div className="bg-gradient-to-br from-navy-800 to-navy-900 border border-navy-700 rounded-2xl p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-navy-700 rounded w-1/3 mb-2" />
          <div className="h-8 bg-navy-700 rounded w-2/3" />
        </div>
      </div>
    );
  }

  const assetsValue = wallet.assets.reduce((sum, asset) => {
    const price = livePrices[asset.ticker] ?? asset.current_price;
    return sum + asset.amount * price;
  }, 0);
  const totalValue = wallet.balance + assetsValue;
  const initialBalance = 100000;
  const isProfit = totalValue >= initialBalance;
  const percentageChange = ((totalValue - initialBalance) / initialBalance) * 100;

  return (
    <>
      <div className="bg-gradient-to-br from-navy-800 to-navy-900 border border-navy-700 rounded-2xl p-6">
        <div className="mb-4">
          <div className="text-sm text-gray-400 mb-1">
            Całkowita wartość portfela
          </div>
          <div className="flex items-baseline gap-3">
            <div className={`text-2xl font-bold ${isProfit ? 'text-trading-green' : 'text-trading-red'}`}>
              $
              {totalValue.toLocaleString("en-US", {
                minimumFractionDigits: 3,
                maximumFractionDigits: 3,
              })}
            </div>
            <div className={`text-sm font-medium ${isProfit ? 'text-trading-green' : 'text-trading-red'}`}>
              {percentageChange > 0 ? "+" : ""}
              {percentageChange.toFixed(3)}%
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-navy-900/50 rounded-xl">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-trading-gold/20 flex items-center justify-center">
                <span className="text-trading-gold font-bold text-xs">$</span>
              </div>
              <div>
                <div className="text-white font-medium text-sm">USD</div>
                <div className="text-gray-500 text-xs">Saldo</div>
              </div>
            </div>
            <div className="text-white font-medium">
              $
              {wallet.balance.toLocaleString("en-US", {
                minimumFractionDigits: 3,
                maximumFractionDigits: 3,
              })}
            </div>
          </div>

          {wallet.assets.map((asset) => {
            const price = livePrices[asset.ticker] ?? asset.current_price;
            const value = asset.amount * price;

            const assetIsProfit = price >= asset.average_buy_price;
            const assetPnLPercent = (asset.is_active && asset.average_buy_price > 0)
              ? ((price - asset.average_buy_price) / asset.average_buy_price) * 100 
              : 0;

            return (
              <div
                key={asset.ticker}
                className="flex items-center justify-between p-3 bg-navy-900/50 rounded-xl"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-trading-cyan/30 to-trading-green/30 flex items-center justify-center">
                    <span className="text-trading-cyan font-bold text-xs">
                      {asset.ticker.slice(0, 2)}
                    </span>
                  </div>
                  <div>
                    <div className="text-white font-medium text-sm">
                      {asset.ticker}
                    </div>
                    <div className="text-gray-500 text-xs">
                      {asset.amount.toFixed(4)}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  {asset.is_active ? (
                    <div className="text-white font-medium text-sm">
                      $
                      {value.toLocaleString("en-US", {
                        minimumFractionDigits: 3,
                        maximumFractionDigits: 3,
                      })}
                    </div>
                  ) : (
                    <div className="text-red-500 text-xs font-medium mb-1">
                      Not Tracked
                    </div>
                  )}
                  <div className={`text-xs ${assetIsProfit ? 'text-trading-green' : 'text-trading-red'}`}>
                    {assetPnLPercent > 0 ? "+" : ""}
                    {assetPnLPercent.toFixed(2)}%
                  </div>
                </div>
              </div>
            );
          })}

          {wallet.assets.length === 0 && (
            <div className="text-center text-gray-500 text-sm py-2">
              Brak posiadanych kryptowalut
            </div>
          )}
        </div>

        {/* Przycisk Reset Konta */}
        <div className="mt-6 pt-4 border-t border-navy-700">
          <button
            onClick={() => setShowResetDialog(true)}
            className="w-full py-2.5 px-4 bg-gradient-to-r from-red-600/20 to-red-500/20 
                       hover:from-red-600/30 hover:to-red-500/30 
                       border border-red-500/30 rounded-xl
                       text-red-400 text-sm font-medium
                       transition-all duration-200
                       flex items-center justify-center gap-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clipRule="evenodd" />
            </svg>
            Resetuj konto
          </button>
        </div>
      </div>

      {/* Dialog potwierdzenia */}
      {showResetDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Backdrop */}
          <div 
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
            onClick={() => !isResetting && setShowResetDialog(false)}
          />
          
          {/* Dialog */}
          <div className="relative bg-gradient-to-br from-navy-800 to-navy-900 border border-navy-600 rounded-2xl p-6 max-w-md w-full mx-4 shadow-2xl">
            {/* Header */}
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-full bg-red-500/20 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">Resetuj konto</h3>
                <p className="text-gray-400 text-sm">Ta akcja jest nieodwracalna</p>
              </div>
            </div>

            {/* Content */}
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 mb-6">
              <p className="text-gray-300 text-sm leading-relaxed">
                <strong className="text-red-400">Uwaga!</strong> Resetowanie konta spowoduje:
              </p>
              <ul className="mt-2 space-y-1 text-sm text-gray-400">
                <li className="flex items-center gap-2">
                  <span className="text-red-400">•</span>
                  Usunięcie całego portfolio (wszystkich kryptowalut)
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-red-400">•</span>
                  Usunięcie całej historii transakcji
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-trading-green">•</span>
                  Przywrócenie salda do <strong className="text-trading-green">$100,000</strong>
                </li>
              </ul>
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <button
                onClick={() => setShowResetDialog(false)}
                disabled={isResetting}
                className="flex-1 py-2.5 px-4 bg-navy-700 hover:bg-navy-600 
                           border border-navy-600 rounded-xl
                           text-white text-sm font-medium
                           transition-all duration-200
                           disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Anuluj
              </button>
              <button
                onClick={handleResetAccount}
                disabled={isResetting}
                className="flex-1 py-2.5 px-4 bg-gradient-to-r from-red-600 to-red-500 
                           hover:from-red-500 hover:to-red-400
                           rounded-xl text-white text-sm font-medium
                           transition-all duration-200
                           disabled:opacity-50 disabled:cursor-not-allowed
                           flex items-center justify-center gap-2"
              >
                {isResetting ? (
                  <>
                    <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Resetowanie...
                  </>
                ) : (
                  "Potwierdź reset"
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
