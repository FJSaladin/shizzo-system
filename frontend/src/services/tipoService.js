import api from './api';

export const tipoService = {
  // Obtener todos los tipos
  getAll: async () => {
    const response = await api.get('/tipos-cotizacion');
    return response.data;
  },
  
  // Obtener tipo por ID
  getById: async (id) => {
    const response = await api.get(`/tipos-cotizacion/${id}`);
    return response.data;
  },
  
  // Crear tipo
  create: async (tipoData) => {
    const response = await api.post('/tipos-cotizacion', tipoData);
    return response.data;
  },
};

// También actualizar cotizacionService.js agregando:
export const cotizacionService = {
  // ... métodos existentes ...
  
  // Cambiar estado
  cambiarEstado: async (id, estado) => {
    const response = await api.patch(`/cotizaciones/${id}/estado`, { estado });
    return response.data;
  },
};