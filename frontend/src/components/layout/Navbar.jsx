import { Bell, User, Search } from 'lucide-react';

export default function Navbar() {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200 h-16 fixed top-0 right-0 left-64 z-10">
      <div className="flex items-center justify-between px-6 h-full">
        {/* Search */}
        <div className="flex-1 max-w-md">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Buscar..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-shizzo focus:border-transparent outline-none"
            />
          </div>
        </div>
        
        {/* Right side */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors relative">
            <Bell size={20} />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </button>
          
          {/* User */}
          <div className="flex items-center space-x-3 pl-4 border-l border-gray-200">
            <div className="text-right">
              <p className="text-sm font-semibold text-gray-900">Usuario Admin</p>
              <p className="text-xs text-gray-500">Administrador</p>
            </div>
            <div className="w-10 h-10 bg-yellow-shizzo rounded-full flex items-center justify-center">
              <User size={20} className="text-gray-900" />
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}