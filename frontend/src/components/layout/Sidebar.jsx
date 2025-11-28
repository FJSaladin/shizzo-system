import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  FileText, 
  FolderKanban, 
  Settings,
  Zap
} from 'lucide-react';

const menuItems = [
  { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/clientes', icon: Users, label: 'Clientes' },
  { path: '/cotizaciones', icon: FileText, label: 'Cotizaciones' },
  { path: '/proyectos', icon: FolderKanban, label: 'Proyectos' },
  { path: '/configuracion', icon: Settings, label: 'Configuración' },
];

export default function Sidebar() {
  const location = useLocation();
  
  return (
    <aside className="w-64 bg-primary text-white flex flex-col h-screen fixed left-0 top-0">
      {/* Logo */}
      <div className="p-6 border-b border-gray-700">
        <div className="flex items-center space-x-3">
          <div className="bg-yellow-shizzo p-2 rounded-lg">
            <Zap className="text-gray-900" size={28} />
          </div>
          <div>
            <h1 className="text-xl font-bold">SHIZZO</h1>
            <p className="text-xs text-gray-400">Sistema Administrativo</p>
          </div>
        </div>
      </div>
      
      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname.startsWith(item.path);
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`
                flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200
                ${isActive 
                  ? 'bg-yellow-shizzo text-gray-900 font-semibold shadow-lg' 
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                }
              `}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
      
      {/* Footer */}
      <div className="p-4 border-t border-gray-700">
        <p className="text-xs text-gray-500 text-center">
          SHIZZO GROUP © 2025
        </p>
      </div>
    </aside>
  );
}