import { useUsuario } from '@/hooks/useUsuario';
import { useAuth } from '@/hooks/useAuth';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  User,
  EnvelopeSimple,
  CalendarBlank,
  CurrencyDollar,
  ShieldCheck,
} from '@phosphor-icons/react';
import { useNavigate } from 'react-router-dom';

export function Profile() {
  const { user, logout } = useAuth();
  const { data: usuario } = useUsuario();
  const navigate = useNavigate();

  return (
    <div className="mx-auto max-w-2xl space-y-8 px-6 py-8">
      <h1 className="text-2xl font-bold">Mi Perfil</h1>

      {/* Avatar + Info */}
      <Card glow>
        <div className="flex flex-col items-center gap-4 sm:flex-row">
          {user?.photoURL && (
            <img
              src={user.photoURL}
              alt="Avatar"
              className="h-20 w-20 rounded-full ring-2 ring-emerald-500/30"
            />
          )}
          <div className="text-center sm:text-left">
            <h2 className="text-xl font-semibold text-slate-100">
              {usuario?.nombre ?? user?.displayName}
            </h2>
            <p className="flex items-center justify-center gap-1.5 text-sm text-slate-400 sm:justify-start">
              <EnvelopeSimple size={14} />
              {usuario?.email ?? user?.email}
            </p>
            <span className="mt-2 inline-block rounded-full bg-emerald-900/50 px-3 py-0.5 text-xs font-medium capitalize text-emerald-300">
              {usuario?.plan_suscripcion ?? 'trial'}
            </span>
          </div>
        </div>
      </Card>

      {/* Details */}
      <Card title="Detalles de cuenta">
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <User size={18} className="text-slate-500" />
            <div>
              <p className="text-xs text-slate-500">ID de usuario</p>
              <p className="font-mono text-sm text-slate-300">#{usuario?.id ?? '—'}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <CalendarBlank size={18} className="text-slate-500" />
            <div>
              <p className="text-xs text-slate-500">Miembro desde</p>
              <p className="text-sm text-slate-300">
                {usuario?.creado_en
                  ? new Date(usuario.creado_en).toLocaleDateString('es-ES', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })
                  : '—'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <CurrencyDollar size={18} className="text-slate-500" />
            <div>
              <p className="text-xs text-slate-500">Plan</p>
              <p className="text-sm capitalize text-slate-300">
                {usuario?.plan_suscripcion ?? 'trial'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <ShieldCheck size={18} className="text-slate-500" />
            <div>
              <p className="text-xs text-slate-500">Estado</p>
              <p className="flex items-center gap-1.5 text-sm text-emerald-400">
                <span className="h-2 w-2 rounded-full bg-emerald-500" />
                {usuario?.activo ? 'Cuenta activa' : 'Cuenta suspendida'}
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Actions */}
      <div className="flex justify-center gap-4">
        <Button variant="secondary" onClick={() => navigate('/settings')}>
          Editar perfil
        </Button>
        <Button variant="ghost" onClick={logout}>
          Cerrar sesión
        </Button>
      </div>
    </div>
  );
}
