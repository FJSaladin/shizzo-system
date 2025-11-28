import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/layout/Layout';
import Dashboard from './pages/dashboard/Dashboard';
import Clientes from './pages/clientes/Clientes';

// Configurar React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/clientes" element={<Clientes />} />
            
            {/* Rutas futuras */}
            <Route path="/cotizaciones" element={<div className="text-center py-12">Cotizaciones - Próximamente</div>} />
            <Route path="/proyectos" element={<div className="text-center py-12">Proyectos - Próximamente</div>} />
            <Route path="/configuracion" element={<div className="text-center py-12">Configuración - Próximamente</div>} />
          </Routes>
        </Layout>
      </Router>
    </QueryClientProvider>
  );
}

export default App;