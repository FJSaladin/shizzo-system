import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Save } from 'lucide-react';
import { clienteService } from '../../services/clienteService';
import Toast from '../../components/common/Toast';

export default function ClienteForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isEditMode = !!id;

  const [formData, setFormData] = useState({
    nombre: '',
    rnc: '',
    correo: '',
    telefono: '',
    direccion: ''
  });

  const [toast, setToast] = useState(null);
  const [errors, setErrors] = useState({});

  // Cargar datos si es modo edición
  useQuery({
    queryKey: ['cliente', id],
    queryFn: () => clienteService.getById(id),
    enabled: isEditMode,
    onSuccess: (data) => {
      setFormData({
        nombre: data.nombre || '',
        rnc: data.rnc || '',
        correo: data.correo || '',
        telefono: data.telefono || '',
        direccion: data.direccion || ''
      });
    }
  });

  // Mutación para crear/actualizar
  const mutation = useMutation({
    mutationFn: (data) => {
      if (isEditMode) {
        return clienteService.update(id, data);
      }
      return clienteService.create(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['clientes']);
      setToast({
        type: 'success',
        message: `Cliente ${isEditMode ? 'actualizado' : 'creado'} exitosamente`
      });
      setTimeout(() => navigate('/clientes'), 1500);
    },
    onError: (error) => {
      setToast({
        type: 'error',
        message: 'Error al guardar el cliente'
      });
      console.error('Error:', error);
    }
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Limpiar error del campo
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };

  const validate = () => {
    const newErrors = {};
    
    if (!formData.nombre.trim()) {
      newErrors.nombre = 'El nombre es requerido';
    }
    
    if (formData.correo && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.correo)) {
      newErrors.correo = 'Email inválido';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validate()) {
      setToast({
        type: 'error',
        message: 'Por favor corrige los errores en el formulario'
      });
      return;
    }
    
    mutation.mutate(formData);
  };

  return (
    <div className="space-y-6">
      {/* Toast */}
      {toast && (
        <Toast
          type={toast.type}
          message={toast.message}
          onClose={() => setToast(null)}
        />
      )}

      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/clientes')}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft size={24} />
        </button>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            {isEditMode ? 'Editar Cliente' : 'Nuevo Cliente'}
          </h1>
          <p className="text-gray-600 mt-1">
            {isEditMode ? 'Actualiza la información del cliente' : 'Completa el formulario para crear un nuevo cliente'}
          </p>
        </div>
      </div>

      {/* Form */}
      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Nombre */}
          <div>
            <label htmlFor="nombre" className="block text-sm font-medium text-gray-700 mb-2">
              Nombre <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="nombre"
              name="nombre"
              value={formData.nombre}
              onChange={handleChange}
              className={`input-field ${errors.nombre ? 'border-red-500' : ''}`}
              placeholder="Nombre del cliente o empresa"
            />
            {errors.nombre && (
              <p className="mt-1 text-sm text-red-500">{errors.nombre}</p>
            )}
          </div>

          {/* RNC */}
          <div>
            <label htmlFor="rnc" className="block text-sm font-medium text-gray-700 mb-2">
              RNC
            </label>
            <input
              type="text"
              id="rnc"
              name="rnc"
              value={formData.rnc}
              onChange={handleChange}
              className="input-field"
              placeholder="1-01-12345-6"
            />
          </div>

          {/* Grid 2 columnas */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Correo */}
            <div>
              <label htmlFor="correo" className="block text-sm font-medium text-gray-700 mb-2">
                Correo Electrónico
              </label>
              <input
                type="email"
                id="correo"
                name="correo"
                value={formData.correo}
                onChange={handleChange}
                className={`input-field ${errors.correo ? 'border-red-500' : ''}`}
                placeholder="correo@ejemplo.com"
              />
              {errors.correo && (
                <p className="mt-1 text-sm text-red-500">{errors.correo}</p>
              )}
            </div>

            {/* Teléfono */}
            <div>
              <label htmlFor="telefono" className="block text-sm font-medium text-gray-700 mb-2">
                Teléfono
              </label>
              <input
                type="tel"
                id="telefono"
                name="telefono"
                value={formData.telefono}
                onChange={handleChange}
                className="input-field"
                placeholder="(809) 555-1234"
              />
            </div>
          </div>

          {/* Dirección */}
          <div>
            <label htmlFor="direccion" className="block text-sm font-medium text-gray-700 mb-2">
              Dirección
            </label>
            <textarea
              id="direccion"
              name="direccion"
              value={formData.direccion}
              onChange={handleChange}
              rows={3}
              className="input-field"
              placeholder="Dirección completa del cliente"
            />
          </div>

          {/* Botones */}
          <div className="flex justify-end space-x-3 pt-6 border-t">
            <button
              type="button"
              onClick={() => navigate('/clientes')}
              className="btn-outline"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={mutation.isPending}
              className="btn-primary flex items-center space-x-2"
            >
              <Save size={20} />
              <span>{mutation.isPending ? 'Guardando...' : 'Guardar'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}