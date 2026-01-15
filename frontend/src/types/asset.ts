export interface Asset {
  id: number;
  ticker: string;
  name: string;
  binance_symbol: string;
  current_price: number;
  is_active: boolean;
}

export interface AssetPrice {
  id: number;
  ticker: string;
  name: string;
  current_price: number;
}

export interface Kline {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface WalletAsset {
  ticker: string;
  name: string;
  amount: number;
  current_price: number;
  value: number;
  average_buy_price: number;
  is_active: boolean;
}

export interface WalletStatus {
  username: string;
  balance: number;
  assets: WalletAsset[];
  total_value: number;
}

export interface TradeRequest {
  asset_ticker: string;
  amount: number;
}

export interface TransactionResponse {
  id: number;
  user_id: number;
  asset_id: number;
  ticker: string;
  amount: number;
  price_at_transaction: number;
  type: string;
  timestamp: string;
}

export interface ResetAccountResponse {
  success: boolean;
  message: string;
  deleted_portfolio_items: number;
  deleted_transactions: number;
  new_balance: number;
}
