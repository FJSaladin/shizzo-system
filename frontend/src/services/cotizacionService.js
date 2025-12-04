import api from './api';

export const cotizacionService = {
  // Obtener todas las cotizaciones
  getAll: async () => {
    const response = await api.get('/cotizaciones');
    return response.data;
  },
  
  // Obtener cotización por ID
  getById: async (id) => {
    const response = await api.get(`/cotizaciones/${id}`);
    return response.data;
  },
  
  // Crear cotización (sin PDF)
  create: async (cotizacionData) => {
    const response = await api.post('/cotizaciones', cotizacionData);
    return response.data;
  },
  
    update: async (id, cotizacionData) => {
    const response = await api.put(`/cotizaciones/${id}`, cotizacionData);
    return response.data;
  },
  // Generar PDF de cotización
  generarPDF: async (id) => {
    const response = await api.post(`/cotizaciones/${id}/generar-pdf`);
    return response.data;
  },
  
  // Cambiar estado
  cambiarEstado: async (id, estado) => {
    const response = await api.patch(`/cotizaciones/${id}/estado`, { estado });
    return response.data;
  },
  
  // Descargar PDF
  downloadPDF: (id) => {
    window.open(`${api.defaults.baseURL}/cotizaciones/${id}/pdf`, '_blank');
  },
  
  // Abrir PDF en nueva pestaña
  openPDF: (id) => {
    window.open(`${api.defaults.baseURL}/cotizaciones/${id}/pdf`, '_blank');
  },
};