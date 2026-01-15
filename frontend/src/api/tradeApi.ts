/**
 * API klient dla operacji handlowych.
 */

import { apiRequest } from './api';
import type { TradeRequest, TransactionResponse, WalletStatus, ResetAccountResponse } from '../types/asset';

/**
 * Wykonuje zakup aktywa.
 */
export async function buyAsset(ticker: string, amount: number): Promise<TransactionResponse> {
  const data: TradeRequest = { asset_ticker: ticker, amount };
  return apiRequest<TransactionResponse>('/trade/buy', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Wykonuje sprzedaż aktywa.
 */
export async function sellAsset(ticker: string, amount: number): Promise<TransactionResponse> {
  const data: TradeRequest = { asset_ticker: ticker, amount };
  return apiRequest<TransactionResponse>('/trade/sell', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * Pobiera stan portfela użytkownika.
 */
export async function getWallet(): Promise<WalletStatus> {
  return apiRequest<WalletStatus>('/trade/wallet');
}

/**
 * Resetuje konto użytkownika do stanu początkowego.
 * Usuwa portfolio, transakcje i przywraca saldo do $100,000.
 */
export async function resetAccount(): Promise<ResetAccountResponse> {
  return apiRequest<ResetAccountResponse>('/trade/reset-account', {
    method: 'POST',
  });
}
