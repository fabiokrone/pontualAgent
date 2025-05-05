'use client';

import axios from 'axios';
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Definir a URL base da API - Usando o nome do serviço conforme configurado no Docker Compose
// Remover barras duplicadas
const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/+$/, '');


// Criar uma instância do axios com configurações padrão
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Adicionar interceptor para incluir o token em todas as requisições
api.interceptors.request.use(
  (config) => {
    // Verifica se está no navegador (não no servidor)
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);


// Adicionar interceptor para tratar erros de autenticação
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Redirecionar para login se o token expirou ou é inválido
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Interface para o contexto da API
interface ApiContextType {
  api: typeof api;
  isLoading: boolean;
  error: string | null;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

// Criar o contexto da API
const ApiContext = createContext<ApiContextType | undefined>(undefined);

// Provider para o contexto da API
export function ApiProvider({ children }: { children: ReactNode }) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const setLoading = (loading: boolean) => {
    setIsLoading(loading);
  };

  const setErrorMessage = (errorMessage: string | null) => {
    setError(errorMessage);
  };

  const value = {
    api,
    isLoading,
    error,
    setLoading,
    setError: setErrorMessage,
  };

  return (
    <ApiContext.Provider value={value}>
      {children}
    </ApiContext.Provider>
  );
}

// Hook para usar o contexto da API
export function useApi() {
  const context = useContext(ApiContext);
  if (context === undefined) {
    throw new Error('useApi deve ser usado dentro de um ApiProvider');
  }
  return context;
}

// Serviços específicos para cada entidade
export const authService = {
  login: async (email: string, password: string) => {
    try {
      const response = await api.post("/api/auth/login", { email, password });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  getMe: async () => {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export const servidoresService = {
  getAll: async (params?: any) => {
    try {
      const response = await api.get('/api/servidores', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  getById: async (id: number) => {
    try {
      const response = await api.get(`/api/servidores/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  create: async (data: any) => {
    try {
      const response = await api.post('/servidores', data);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  update: async (id: number, data: any) => {
    try {
      const response = await api.put(`/servidores/${id}`, data);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  delete: async (id: number) => {
    try {
      const response = await api.delete(`/servidores/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export const batidasService = {
  getAll: async (params?: any) => {
    try {
      const response = await api.get('/batidas', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  importar: async (file: File) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await api.post('/batidas/importar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  getEspelhoPonto: async (matricula: string, mesAno: string) => {
    try {
      const response = await api.get(`/batidas/espelho-ponto`, {
        params: { matricula, mes_ano: mesAno },
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export const justificativasService = {
  getAll: async (params?: any) => {
    try {
      const response = await api.get('/justificativas', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  getById: async (id: number) => {
    try {
      const response = await api.get(`/justificativas/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  create: async (data: any) => {
    try {
      const response = await api.post('/justificativas', data);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  aprovar: async (id: number, observacao?: string) => {
    try {
      const response = await api.post(`/justificativas/${id}/aprovar`, { observacao });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  rejeitar: async (id: number, observacao?: string) => {
    try {
      const response = await api.post(`/justificativas/${id}/rejeitar`, { observacao });
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export const dashboardService = {
  getStats: async () => {
    try {
      const response = await api.get('/api/dashboard/stats');
      return response.data;
    } catch (error) {
      throw error;
    }
  },
  
  getRecentActivities: async () => {
    try {
      const response = await api.get('/api/dashboard/recent-activities');
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

export default api;
