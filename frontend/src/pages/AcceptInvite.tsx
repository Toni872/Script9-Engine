import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { GlassCard } from '@/components/ui/GlassCard';
import { Button } from '@/components/ui/Button';
import { CheckCircle, XCircle } from '@phosphor-icons/react';

export function AcceptInvite() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setError('Token de invitación no proporcionado');
      return;
    }

    fetch(`/api/v1/invitations/accept?token=${encodeURIComponent(token)}`)
      .then(res => {
        if (!res.ok) throw new Error('Token inválido o expirado');
        setStatus('success');
      })
      .catch(err => {
        setStatus('error');
        setError(err.message);
      });
  }, [token]);

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-6">
      <GlassCard className="max-w-md w-full p-8 text-center">
        {status === 'loading' && (
          <div className="flex flex-col items-center gap-4">
            <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-slate-400">Verificando invitación...</p>
          </div>
        )}
        {status === 'success' && (
          <div className="flex flex-col items-center gap-4">
            <CheckCircle size={64} className="text-emerald-400" />
            <h2 className="text-2xl font-bold font-space text-white">¡Bienvenido!</h2>
            <p className="text-slate-400">Tu cuenta ha sido activada. Ya puedes empezar a usar Script9 Engine.</p>
            <Button variant="primary" onClick={() => window.location.href = '/dashboard'}>
              Ir al dashboard
            </Button>
          </div>
        )}
        {status === 'error' && (
          <div className="flex flex-col items-center gap-4">
            <XCircle size={64} className="text-red-400" />
            <h2 className="text-2xl font-bold font-space text-white">Invitación inválida</h2>
            <p className="text-slate-400">{error}</p>
            <Button variant="secondary" onClick={() => window.location.href = '/planes'}>
              Volver a Planes
            </Button>
          </div>
        )}
      </GlassCard>
    </div>
  );
}
