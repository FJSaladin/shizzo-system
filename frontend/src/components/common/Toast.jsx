import { CheckCircle, AlertCircle, X } from 'lucide-react';
import { useEffect } from 'react';

export default function Toast({ type = 'success', message, onClose, duration = 3000 }) {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const types = {
    success: {
      icon: CheckCircle,
      bgColor: 'bg-green-50',
      textColor: 'text-green-800',
      iconColor: 'text-green-600',
      borderColor: 'border-green-200'
    },
    error: {
      icon: AlertCircle,
      bgColor: 'bg-red-50',
      textColor: 'text-red-800',
      iconColor: 'text-red-600',
      borderColor: 'border-red-200'
    }
  };

  const config = types[type];
  const Icon = config.icon;

  return (
    <div className={`fixed top-4 right-4 z-50 ${config.bgColor} ${config.textColor} border ${config.borderColor} rounded-lg shadow-lg p-4 flex items-center space-x-3 animate-slideIn`}>
      <Icon className={config.iconColor} size={20} />
      <p className="font-medium">{message}</p>
      <button onClick={onClose} className="ml-4">
        <X size={18} />
      </button>
    </div>
  );
}