import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

export function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'bg-slate-950/80 backdrop-blur-md border-b border-slate-800/50'
          : 'bg-transparent'
      }`}
    >
      <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        <Link to="/" className="logo-script9">
          <span className="script">Script</span>
          <span className="nine">9</span>
        </Link>

        {user && (
          <div className="flex items-center gap-4">
            <div className="hidden items-center gap-3 sm:flex">
              {user.photoURL && (
                <img
                  src={user.photoURL}
                  alt=""
                  className="h-8 w-8 rounded-full ring-2 ring-emerald-500/30"
                />
              )}
              <span className="text-sm font-medium text-slate-200">
                {user.displayName}
              </span>
            </div>
            <button
              onClick={handleLogout}
              className="rounded-lg px-3 py-1.5 text-sm text-slate-400 transition-colors hover:bg-slate-800/50 hover:text-slate-200"
            >
              Salir
            </button>
          </div>
        )}
      </nav>
    </header>
  );
}
