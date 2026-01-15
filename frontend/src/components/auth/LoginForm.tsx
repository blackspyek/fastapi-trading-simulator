import { useState, type FormEvent } from 'react';
import { useAuth } from '../../context/AuthContext';
import { ApiError } from '../../api/api';

interface LoginFormProps {
  onSuccess?: () => void;
}

export function LoginForm({ onSuccess }: LoginFormProps) {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login({ username, password });
      onSuccess?.();
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Wystąpił błąd podczas logowania');
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <h2 className="text-2xl font-bold text-center mb-8 bg-gradient-to-r from-trading-cyan to-trading-green bg-clip-text text-transparent">
        Zaloguj się
      </h2>

      {error && (
        <div className="mb-6 p-4 bg-trading-red/10 border border-trading-red/30 rounded-xl text-trading-red text-sm text-center">
          {error}
        </div>
      )}

      <div className="space-y-5">
        <div>
          <label htmlFor="login-username" className="block text-sm font-medium text-gray-400 mb-2">
            Nazwa użytkownika
          </label>
          <input
            id="login-username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Wpisz nazwę użytkownika"
            required
            autoComplete="username"
            className="w-full px-4 py-3 bg-navy-800/50 border border-navy-700 rounded-xl text-white placeholder-gray-500 transition-all duration-200 hover:border-navy-600 focus:border-trading-cyan"
          />
        </div>

        <div>
          <label htmlFor="login-password" className="block text-sm font-medium text-gray-400 mb-2">
            Hasło
          </label>
          <input
            id="login-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Wpisz hasło"
            required
            autoComplete="current-password"
            className="w-full px-4 py-3 bg-navy-800/50 border border-navy-700 rounded-xl text-white placeholder-gray-500 transition-all duration-200 hover:border-navy-600 focus:border-trading-cyan"
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full mt-8 py-3.5 px-6 bg-gradient-to-r from-trading-cyan to-trading-green text-navy-950 font-semibold rounded-xl transition-all duration-200 hover:shadow-lg hover:shadow-trading-cyan/25 hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:hover:shadow-none cursor-pointer"
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Logowanie...
          </span>
        ) : (
          'Zaloguj się'
        )}
      </button>
    </form>
  );
}
