import { Link } from 'react-router-dom';

export function NotFound() {
  return (
    <div className="flex min-h-[calc(100vh-4rem)] flex-col items-center justify-center gap-6">
      <span className="font-mono text-8xl font-bold text-slate-800">404</span>
      <p className="text-lg text-slate-400">Página no encontrada</p>
      <Link to="/" className="btn-primary">
        Volver al inicio
      </Link>
    </div>
  );
}
