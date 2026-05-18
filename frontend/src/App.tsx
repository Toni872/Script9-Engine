import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from '@/components/ui/ProtectedRoute';
import { AppLayout } from '@/components/layout/AppLayout';
import { Login } from '@/pages/Login';
import { Dashboard } from '@/pages/Dashboard';
import { Settings } from '@/pages/Settings';
import { Profile } from '@/pages/Profile';
import { NotFound } from '@/pages/NotFound';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Ruta pública */}
        <Route path="/login" element={<Login />} />

        {/* Rutas protegidas con layout */}
        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/profile" element={<Profile />} />
        </Route>

        {/* Redirects */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
