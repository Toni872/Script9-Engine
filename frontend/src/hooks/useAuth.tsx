import {
  useState,
  useEffect,
  useCallback,
  createContext,
  useContext,
  type ReactNode,
} from 'react';
import {
  onAuthStateChanged,
  signInWithPopup,
  signOut,
  type User,
} from 'firebase/auth';
import { auth, googleProvider } from '@/lib/firebase';

// ── Tipos ───────────────────────────────────────────────────
interface AuthState {
  user: User | null;
  isLoading: boolean;
  error: string | null;
}

interface AuthContextValue extends AuthState {
  loginWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
  getIdToken: () => Promise<string | null>;
}

// ── Context ─────────────────────────────────────────────────
const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    error: null,
  });

  // Escucha cambios de sesión
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(
      auth,
      (user) => {
        setState({ user, isLoading: false, error: null });
      },
      (error) => {
        setState((prev) => ({ ...prev, isLoading: false, error: error.message }));
      },
    );
    return unsubscribe;
  }, []);

  // Login con Google
  const loginWithGoogle = useCallback(async () => {
    try {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));
      await signInWithPopup(auth, googleProvider);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al iniciar sesión';
      setState((prev) => ({ ...prev, isLoading: false, error: message }));
      throw err;
    }
  }, []);

  // Logout
  const logout = useCallback(async () => {
    try {
      await signOut(auth);
      setState({ user: null, isLoading: false, error: null });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Error al cerrar sesión';
      setState((prev) => ({ ...prev, error: message }));
    }
  }, []);

  // Obtener token JWT actual (para enviar al backend)
  const getIdToken = useCallback(async (): Promise<string | null> => {
    try {
      return (await auth.currentUser?.getIdToken(true)) ?? null;
    } catch {
      return null;
    }
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, loginWithGoogle, logout, getIdToken }}>
      {children}
    </AuthContext.Provider>
  );
}

// ── Hook ────────────────────────────────────────────────────
export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de un AuthProvider');
  }
  return context;
}

// Tipo exportado para usar en otros hooks/componentes
export type { AuthContextValue };
