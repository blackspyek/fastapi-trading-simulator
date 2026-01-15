import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  getAllAssets,
  createAsset,
  updateAsset,
  toggleAsset,
  deleteAsset,
} from '../api/assetsApi';
import type { Asset } from '../types/asset';

export function AdminAssetsPage() {
  const { logout } = useAuth();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null);
  const [formData, setFormData] = useState({
    ticker: '',
    name: '',
    binance_symbol: '',
  });

  useEffect(() => {
    loadAssets();
  }, []);

  async function loadAssets() {
    try {
      setIsLoading(true);
      const data = await getAllAssets();
      setAssets(data);
      setError(null);
    } catch (err) {
      console.error('Failed to load assets:', err);
      setError('Nie udało się pobrać listy aktywów.');
    } finally {
      setIsLoading(false);
    }
  }

  async function handleToggle(id: number) {
    try {
      const updated = await toggleAsset(id);
      setAssets((prev) => prev.map((a) => (a.id === id ? updated : a)));
    } catch (err) {
      console.error('Failed to toggle asset:', err);
      alert('Błąd podczas zmiany statusu');
    }
  }

  async function handleDelete(id: number) {
    if (
      !confirm(
        'UWAGA! Czy na pewno chcesz usunąć to aktywo?\n\n' +
        'Ta operacja jest nieodwracalna i spowoduje:\n' +
        '- Usunięcie aktywa z systemu\n' +
        '- Usunięcie wszystkich powiązanych transakcji użytkowników\n' +
        '- Usunięcie aktywa ze wszystkich portfeli użytkowników\n\n' +
        'Czy potwierdzasz usunięcie?'
      )
    ) {
      return;
    }

    try {
      await deleteAsset(id);
      setAssets((prev) => prev.filter((a) => a.id !== id));
    } catch (err) {
      console.error('Failed to delete asset:', err);
      alert('Nie udało się usunąć aktywa. Sprawdź logi.');
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      if (editingAsset) {
        const updated = await updateAsset(editingAsset.id, {
          name: formData.name,
          binance_symbol: formData.binance_symbol,
        });
        setAssets((prev) =>
          prev.map((a) => (a.id === editingAsset.id ? updated : a))
        );
      } else {
        const created = await createAsset(formData);
        setAssets((prev) => [...prev, created]);
      }
      closeModal();
    } catch (err) {
      console.error('Failed to save asset:', err);
      alert('Błąd zapisu aktywa. Sprawdź poprawność danych.');
    }
  }

  function openModal(asset?: Asset) {
    if (asset) {
      setEditingAsset(asset);
      setFormData({
        ticker: asset.ticker,
        name: asset.name,
        binance_symbol: asset.binance_symbol,
      });
    } else {
      setEditingAsset(null);
      setFormData({ ticker: '', name: '', binance_symbol: '' });
    }
    setIsModalOpen(true);
  }

  function closeModal() {
    setIsModalOpen(false);
    setEditingAsset(null);
    setFormData({ ticker: '', name: '', binance_symbol: '' });
  }

  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-navy-950 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div className="flex items-center gap-4">
            <Link
              to="/"
              className="px-4 py-2 bg-navy-800 text-gray-300 rounded-lg hover:bg-navy-700 transition-colors"
            >
              &larr; Powrót
            </Link>
            <h1 className="text-2xl font-bold text-white">
              Zarządzanie Kryptowalutami
            </h1>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => openModal()}
              className="px-4 py-2 bg-trading-cyan/10 text-trading-cyan border border-trading-cyan/50 rounded-lg hover:bg-trading-cyan/20 transition-colors cursor-pointer"
            >
              + Dodaj Kryptowalutę
            </button>
            <button
              onClick={logout}
              className="px-4 py-2 bg-trading-red/10 text-trading-red border border-trading-red/30 rounded-lg hover:bg-trading-red/20 transition-colors cursor-pointer"
            >
              Wyloguj
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-trading-red/10 border border-trading-red/50 text-trading-red p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Table */}
        <div className="bg-navy-800/50 backdrop-blur-xl rounded-2xl border border-navy-700 overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-navy-700 bg-navy-900/50">
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Ticker
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Nazwa
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Symbol Binance
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Cena (USD)
                </th>
                <th className="px-6 py-4 text-center text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Akcje
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-700">
              {assets.map((asset) => (
                <tr
                  key={asset.id}
                  className="hover:bg-navy-800/50 transition-colors"
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-trading-cyan">
                    {asset.ticker}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                    {asset.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400 font-mono">
                    {asset.binance_symbol}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-white">
                    {asset.current_price ? (
                      `$${Number(asset.current_price).toLocaleString('en-US', {
                        minimumFractionDigits: 3,
                        maximumFractionDigits: 3,
                      })}`
                    ) : (
                      <span className="text-gray-500">---</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    <button
                      onClick={() => handleToggle(asset.id)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors cursor-pointer ${
                        asset.is_active ? 'bg-trading-green' : 'bg-navy-600'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          asset.is_active ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => openModal(asset)}
                      className="text-trading-cyan hover:text-white mr-4 transition-colors cursor-pointer"
                    >
                      Edytuj
                    </button>
                    <button
                      onClick={() => handleDelete(asset.id)}
                      className="text-trading-red hover:text-white transition-colors cursor-pointer"
                    >
                      Usuń
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {assets.length === 0 && !isLoading && (
            <div className="p-8 text-center text-gray-400">
              Brak zdefiniowanych kryptowalut.
            </div>
          )}
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="bg-navy-800 rounded-2xl border border-navy-700 w-full max-w-md p-6 shadow-xl">
            <h2 className="text-xl font-bold text-white mb-6">
              {editingAsset ? 'Edytuj Kryptowalutę' : 'Dodaj Kryptowalutę'}
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">
                  Ticker (np. BTC)
                </label>
                <input
                  type="text"
                  required
                  disabled={!!editingAsset}
                  value={formData.ticker}
                  onChange={(e) =>
                    setFormData({ ...formData, ticker: e.target.value })
                  }
                  className="w-full bg-navy-900 border border-navy-600 rounded-lg px-4 py-2 text-white focus:border-trading-cyan disabled:opacity-50"
                  placeholder="BTC"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">
                  Nazwa (np. Bitcoin)
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({ ...formData, name: e.target.value })
                  }
                  className="w-full bg-navy-900 border border-navy-600 rounded-lg px-4 py-2 text-white focus:border-trading-cyan"
                  placeholder="Bitcoin"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">
                  Symbol Binance (np. BTCUSDT)
                </label>
                <input
                  type="text"
                  required
                  value={formData.binance_symbol}
                  onChange={(e) =>
                    setFormData({ ...formData, binance_symbol: e.target.value })
                  }
                  className="w-full bg-navy-900 border border-navy-600 rounded-lg px-4 py-2 text-white focus:border-trading-cyan"
                  placeholder="BTCUSDT"
                />
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={closeModal}
                  className="px-4 py-2 text-gray-400 hover:text-white transition-colors cursor-pointer"
                >
                  Anuluj
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-trading-cyan/20 text-trading-cyan border border-trading-cyan/50 rounded-lg hover:bg-trading-cyan/30 transition-colors cursor-pointer"
                >
                  {editingAsset ? 'Zapisz zmiany' : 'Dodaj'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
