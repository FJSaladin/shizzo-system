import { useQuery } from '@tanstack/react-query';
import { Users, FileText, TrendingUp, DollarSign } from 'lucide-react';
import api from '../../services/api';

export default function Dashboard() {
  // Obtener estadísticas del dashboard
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await api.get('/dashboard/stats');
      return response.data;
    }
  });
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-600">Cargando estadísticas...</div>
      </div>
    );
  }
  
  const statCards = [
    { 
      title: 'Total Clientes', 
      value: stats?.total_clientes || 0, 
      icon: Users, 
      color: 'bg-blue-500',
      change: '+12%' 
    },
    { 
      title: 'Cotizaciones', 
      value: stats?.total_cotizaciones || 0, 
      icon: FileText, 
      color: 'bg-green-500',
      change: '+23%' 
    },
    { 
      title: 'Cotizaciones (Mes)', 
      value: stats?.cotizaciones_mes || 0, 
      icon: TrendingUp, 
      color: 'bg-yellow-500',
      change: '+8%' 
    },
    { 
      title: 'Monto Total (Mes)', 
      value: `DOP $${(stats?.monto_total_mes || 0).toLocaleString('es-DO')}`, 
      icon: DollarSign, 
      color: 'bg-purple-500',
      change: '+15%' 
    },
  ];
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Bienvenido al sistema SHIZZO</p>
      </div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, idx) => {
          const Icon = stat.icon;
          return (
            <div key={idx} className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{stat.title}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                  <p className="text-sm text-green-600 mt-1">{stat.change} vs mes anterior</p>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="text-white" size={24} />
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="card-header">Cotizaciones Recientes</h3>
          <div className="space-y-3">
            <div className="text-center py-8 text-gray-500">
              No hay cotizaciones recientes
            </div>
          </div>
        </div>
        
        <div className="card">
          <h3 className="card-header">Clientes Recientes</h3>
          <div className="space-y-3">
            <div className="text-center py-8 text-gray-500">
              No hay clientes recientes
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}