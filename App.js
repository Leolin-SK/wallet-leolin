/**
 * App.js — Point d'entrée React
 * Gestion du routing et de l'authentification
 */

import { useAuth, AuthProvider } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';

function AppContent() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) return (
    <div style={{
      minHeight: '100vh', background: '#080d1a',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: "'DM Sans','Segoe UI',sans-serif"
    }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 64, marginBottom: 20 }}>💰</div>
        <div style={{ fontSize: 18, color: '#818cf8', fontWeight: 700 }}>Wallet Léolin</div>
        <div style={{ fontSize: 13, color: '#475569', marginTop: 8 }}>Chargement...</div>
      </div>
    </div>
  );

  return isAuthenticated ? <Dashboard /> : <LoginPage />;
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
