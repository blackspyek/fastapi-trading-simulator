import { Link, useNavigate } from 'react-router-dom';
import { LoginForm } from '../components/auth/LoginForm';

export function LoginPage() {
  const navigate = useNavigate();

  function handleSuccess() {
    navigate('/');
  }

  return (
    <div className="min-h-screen flex bg-navy-950 relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 -left-32 w-96 h-96 bg-trading-cyan/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-trading-green/10 rounded-full blur-3xl animate-pulse delay-1000" />
        
        <div className="absolute inset-0 bg-[linear-gradient(rgba(0,212,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,212,255,0.03)_1px,transparent_1px)] bg-[size:60px_60px]" />
        
        <svg className="absolute bottom-0 left-0 w-full h-1/2 opacity-20" preserveAspectRatio="none">
          <path
            d="M0,200 Q100,150 200,180 T400,120 T600,160 T800,100 T1000,140 T1200,80 T1400,120 T1600,60 T1920,100"
            fill="none"
            stroke="url(#gradient1)"
            strokeWidth="2"
            className="animate-pulse"
          />
          <path
            d="M0,250 Q150,200 300,230 T600,170 T900,210 T1200,150 T1500,190 T1920,130"
            fill="none"
            stroke="url(#gradient2)"
            strokeWidth="2"
            className="animate-pulse delay-500"
          />
          <defs>
            <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#00d4ff" />
              <stop offset="100%" stopColor="#00d26a" />
            </linearGradient>
            <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#00d26a" />
              <stop offset="100%" stopColor="#ffd700" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      <div className="hidden lg:flex lg:w-1/2 flex-col justify-center items-center p-12 relative z-10">
        <div className="max-w-md text-center lg:text-left">
          <div className="flex items-center gap-3 mb-8 justify-center lg:justify-start">
            <div className="w-14 h-14 bg-gradient-to-br from-trading-cyan to-trading-green rounded-xl flex items-center justify-center shadow-lg shadow-trading-cyan/20">
              <svg className="w-8 h-8 text-navy-950" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
            <span className="text-2xl font-bold text-white">TradingSimulator</span>
          </div>
          
          <h1 className="text-4xl lg:text-5xl font-bold text-white mb-6 leading-tight">
            Naucz się handlować{' '}
            <span className="bg-gradient-to-r from-trading-cyan to-trading-green bg-clip-text text-transparent">
              bez ryzyka
            </span>
          </h1>
          
          <p className="text-gray-400 text-lg mb-8">
            Symulator tradingu kryptowalut z rzeczywistymi danymi rynkowymi. Testuj strategie, buduj portfolio i rozwijaj umiejętności.
          </p>

          <div className="flex flex-wrap gap-4 justify-center lg:justify-start">
            <div className="flex items-center gap-2 text-gray-400">
              <div className="w-2 h-2 bg-trading-green rounded-full" />
              <span>Dane real-time</span>
            </div>
            <div className="flex items-center gap-2 text-gray-400">
              <div className="w-2 h-2 bg-trading-cyan rounded-full" />
              <span>$100k wirtualne</span>
            </div>
            <div className="flex items-center gap-2 text-gray-400">
              <div className="w-2 h-2 bg-trading-gold rounded-full" />
              <span>Zero ryzyka</span>
            </div>
          </div>
        </div>
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
            <LoginForm onSuccess={handleSuccess} />
          </div>

          <p className="mt-8 text-center text-gray-400">
            Nie masz konta?{' '}
            <Link 
              to="/register" 
              className="text-trading-cyan hover:text-trading-green font-medium transition-colors"
            >
              Zarejestruj się
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
