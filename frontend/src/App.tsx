import { useAuth } from '@/hooks/useAuth';

function App() {
  const { user, isLoading, loginWithGoogle, logout } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <p className="text-slate-400 font-mono text-sm animate-pulse">Cargando sesión...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 flex flex-col items-center justify-center gap-6">
      {user ? (
        <>
          <img
            src={user.photoURL ?? ''}
            alt="avatar"
            className="w-16 h-16 rounded-full ring-2 ring-emerald-500/50"
          />
          <p className="text-lg font-medium">
            Hola, <span className="text-emerald-400">{user.displayName}</span>
          </p>
          <p className="text-sm text-slate-400">{user.email}</p>
          <button onClick={logout} className="btn-secondary text-sm">
            Cerrar sesión
          </button>
        </>
      ) : (
        <>
          <div className="flex items-center gap-3 mb-4">
            <span className="logo-script9">
              <span className="script">Script</span>
              <span className="nine">9</span>
            </span>
          </div>
          <p className="text-slate-400 text-sm mb-2">Automatización Inteligente B2B</p>
          <button onClick={loginWithGoogle} className="btn-primary">
            Continuar con Google
          </button>
          {user === null && !isLoading && (
            <p className="text-slate-500 text-xs mt-4">Sesión iniciada como: NO</p>
          )}
        </>
      )}
    </div>
  );
}

export default App;
