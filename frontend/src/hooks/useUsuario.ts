import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api-client';
import { useAuth } from '@/hooks/useAuth';
import type { Usuario } from '@/lib/zod-schemas';

const USUARIO_KEY = ['usuario', 'me'] as const;

export function useUsuario() {
  const { user } = useAuth();

  return useQuery({
    queryKey: USUARIO_KEY,
    queryFn: () => api.getMe(),
    enabled: !!user,            // solo se ejecuta si hay sesión
    staleTime: 5 * 60 * 1000,  // 5 min (coincide con QueryClient global)
    retry: 2,
  });
}

export type { Usuario };
