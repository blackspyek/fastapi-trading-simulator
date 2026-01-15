import { apiRequest } from './api';
import type { UserRegister, UserLogin, Token, User } from '../types/auth';

export async function register(data: UserRegister): Promise<User> {
  return apiRequest<User>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function login(data: UserLogin): Promise<Token> {
  return apiRequest<Token>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getCurrentUser(): Promise<User> {
  return apiRequest<User>('/auth/me');
}
