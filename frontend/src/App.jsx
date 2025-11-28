import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';  // ← Cambiar aquí

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
        <div className="min-h-screen bg-gray-100">
          <div className="flex items-center justify-center h-screen">
            <div className="text-center">
              <h1 className="text-4xl font-bold text-gray-900 mb-4">
                🎉 SHIZZO System
              </h1>
              <p className="text-gray-600 text-lg mb-8">
                Frontend funcionando correctamente
              </p>
              <div className="inline-block bg-yellow-shizzo text-gray-900 px-6 py-3 rounded-lg font-semibold shadow-lg">
                ✅ React + Vite + Tailwind v3
              </div>
            </div>
          </div>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;