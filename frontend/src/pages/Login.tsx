import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/Button';
import { Cube3D } from '@/components/ui/Cube3D';
import { GoogleLogo } from '@phosphor-icons/react';

export function Login() {
  const { user, isLoading, loginWithGoogle } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) navigate('/dashboard', { replace: true });
  }, [user, navigate]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950">
        <p className="font-mono text-sm text-slate-400 animate-pulse">
          Cargando sesión...
        </p>
      </div>
    );
  }

  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center bg-slate-950 overflow-hidden">
      <div className="tech-grid absolute inset-0" />
      <div className="aura-glow absolute -inset-40 top-1/3" />

      <div className="relative z-10 flex flex-col items-center gap-8">
        <div className="logo-script9 text-5xl">
          <span className="script">Script</span>
          <span className="nine">9</span>
        </div>
        <p className="text-center text-sm text-slate-400">
          Automatización Inteligente B2B
        </p>
        <Cube3D />
        <Button
          variant="primary"
          size="lg"
          leftIcon={<GoogleLogo size={20} weight="bold" />}
          onClick={loginWithGoogle}
        >
          Continuar con Google
        </Button>
      </div>
    </div>
  );
}
