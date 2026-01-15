import { apiRequest } from './api';
import type { AssetPrice, Asset, Kline } from '../types/asset';

export async function getAssets(): Promise<AssetPrice[]> {
  return apiRequest<AssetPrice[]>('/assets/');
}

export async function getAsset(id: number): Promise<Asset> {
  return apiRequest<Asset>(`/assets/${id}`);
}

export async function getAssetKlines(
  id: number,
  interval: string = '1h',
  limit: number = 100
): Promise<Kline[]> {
  return apiRequest<Kline[]>(`/assets/${id}/klines?interval=${interval}&limit=${limit}`);
}

export async function getAllAssets(): Promise<Asset[]> {
  return apiRequest<Asset[]>('/assets/admin/all');
}

export async function createAsset(data: {
  ticker: string;
  name: string;
  binance_symbol: string;
}): Promise<Asset> {
  return apiRequest<Asset>('/assets/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateAsset(
  id: number,
  data: { name?: string; binance_symbol?: string; is_active?: boolean }
): Promise<Asset> {
  return apiRequest<Asset>(`/assets/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function toggleAsset(id: number): Promise<Asset> {
  return apiRequest<Asset>(`/assets/${id}/toggle`, {
    method: 'PATCH',
  });
}

export async function deleteAsset(id: number): Promise<void> {
  return apiRequest<void>(`/assets/${id}`, {
    method: 'DELETE',
  });
}
