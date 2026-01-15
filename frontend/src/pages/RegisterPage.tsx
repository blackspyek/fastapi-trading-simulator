import { Link, useNavigate } from 'react-router-dom';
import { RegisterForm } from '../components/auth/RegisterForm';

export function RegisterPage() {
  const navigate = useNavigate();

  function handleSuccess() {
    navigate('/');
  }

  return (
    <div className="min-h-screen flex bg-navy-950 relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 -right-32 w-96 h-96 bg-trading-green/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 -left-32 w-96 h-96 bg-trading-cyan/10 rounded-full blur-3xl animate-pulse delay-1000" />
        
        <div className="absolute inset-0 bg-[linear-gradient(rgba(0,210,106,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,210,106,0.03)_1px,transparent_1px)] bg-[size:60px_60px]" />
        
        <svg className="absolute bottom-0 left-0 w-full h-1/2 opacity-20" preserveAspectRatio="none">
          <path
            d="M0,200 Q100,150 200,180 T400,120 T600,160 T800,100 T1000,140 T1200,80 T1400,120 T1600,60 T1920,100"
            fill="none"
            stroke="url(#gradient1)"
            strokeWidth="2"
            className="animate-pulse"
          />
          <defs>
            <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#00d26a" />
              <stop offset="100%" stopColor="#00d4ff" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 sm:p-12 relative z-10">
        <div className="w-full max-w-md">
          <div className="flex items-center justify-center gap-3 mb-10 lg:hidden">
            <div className="w-12 h-12 bg-gradient-to-br from-trading-cyan to-trading-green rounded-xl flex items-center justify-center">
              <svg className="w-7 h-7 text-navy-950" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <span className="text-xl font-bold text-white">TradingSimulator</span>
          </div>

          <div className="bg-navy-900/50 backdrop-blur-xl border border-navy-700/50 rounded-2xl p-8 shadow-2xl">
            <RegisterForm onSuccess={handleSuccess} />
          </div>

          <p className="mt-8 text-center text-gray-400">
            Masz już konto?{' '}
            <Link 
              to="/login" 
              className="text-trading-cyan hover:text-trading-green font-medium transition-colors"
            >
              Zaloguj się
            </Link>
          </p>
        </div>
      </div>

      <div className="hidden lg:flex lg:w-1/2 flex-col justify-center items-center p-12 relative z-10">
        <div className="max-w-md text-center lg:text-left">
          <div className="flex items-center gap-3 mb-8 justify-center lg:justify-start">
            <div className="w-14 h-14 bg-gradient-to-br from-trading-cyan to-trading-green rounded-xl flex items-center justify-center shadow-lg shadow-trading-green/20">
              <svg className="w-8 h-8 text-navy-950" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <span className="text-2xl font-bold text-white">TradingSimulator</span>
          </div>
          
          <h1 className="text-4xl lg:text-5xl font-bold text-white mb-6 leading-tight">
            Dołącz do{' '}
            <span className="bg-gradient-to-r from-trading-green to-trading-cyan bg-clip-text text-transparent">
              społeczności
            </span>{' '}
            traderów
          </h1>
          
          <p className="text-gray-400 text-lg mb-8">
            Załóż darmowe konto i zacznij swoją przygodę z tradingiem. Otrzymujesz $100,000 wirtualnego kapitału.
          </p>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-navy-800/50 border border-navy-700/50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-trading-green mb-1">$100k</div>
              <div className="text-sm text-gray-400">Kapitał startowy</div>
            </div>
            <div className="bg-navy-800/50 border border-navy-700/50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-trading-cyan mb-1">24/7</div>
              <div className="text-sm text-gray-400">Dostępność</div>
            </div>
            <div className="bg-navy-800/50 border border-navy-700/50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-trading-gold mb-1">10+</div>
              <div className="text-sm text-gray-400">Kryptowalut</div>
            </div>
            <div className="bg-navy-800/50 border border-navy-700/50 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-white mb-1">0%</div>
              <div className="text-sm text-gray-400">Ryzyka finansowego</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
