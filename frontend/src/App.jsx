import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/layout/Layout';
import Dashboard from './pages/dashboard/Dashboard';
import Clientes from './pages/clientes/Clientes';
import ClienteForm from './pages/clientes/ClienteForm';
import Cotizaciones from './pages/cotizaciones/Cotizaciones';
import CotizacionForm from './pages/cotizaciones/CotizacionForm';


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
            
            {/* Clientes */}
            <Route path="/clientes" element={<Clientes />} />
            <Route path="/clientes/nuevo" element={<ClienteForm />} />
            <Route path="/clientes/editar/:id" element={<ClienteForm />} />
            
            {/* Cotizaciones */}
            <Route path="/cotizaciones" element={<Cotizaciones />} />
            <Route path="/cotizaciones/nueva" element={<CotizacionForm />} />
            <Route path="/cotizaciones/:id" element={<div>Detalle próximamente</div>} />
            
            <Route path="/proyectos" element={<div className="text-center py-12">Proyectos - Próximamente</div>} />
            <Route path="/configuracion" element={<div className="text-center py-12">Configuración - Próximamente</div>} />
          </Routes>
        </Layout>
      </Router>
    </QueryClientProvider>
  );
}

export default App;