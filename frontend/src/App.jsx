import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/layout/Layout';
import Dashboard from './pages/dashboard/Dashboard';
import Clientes from './pages/clientes/Clientes';
import ClienteForm from './pages/clientes/ClienteForm';

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
  console.log('App renderizando...');
  
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            
            {/* Clientes */}
            <Route path="/clientes" element={<Clientes />} />
            <Route 
              path="/clientes/nuevo" 
              element={
                <>
                  {console.log('Renderizando ClienteForm nuevo')}
                  <ClienteForm />
                </>
              } 
            />
            <Route 
              path="/clientes/editar/:id" 
              element={
                <>
                  {console.log('Renderizando ClienteForm editar')}
                  <ClienteForm />
                </>
              } 
            />
            
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