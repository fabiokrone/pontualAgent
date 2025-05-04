'use client';
import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';

// Interface para o contexto de autenticação
interface AuthContextType {
  user: any | null;
  token: string | null;
  login: (token: string, userData: any) => void;
  logout: () => void;
  isLoading: boolean;
}

// Criação do contexto
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider de autenticação
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<any | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    // Verificar se há um token no localStorage
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      // Aqui podemos fazer uma requisição para obter os dados do usuário
      // usando o token armazenado
      fetchUserData(storedToken);
    } else {
      setIsLoading(false);
    }
  }, []);
  
  const fetchUserData = async (token: string) => {
    try {
      // Usar URL relativa para o endpoint de autenticação
      const response = await fetch('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      // Verificar se a resposta é JSON válido
      let userData;
      try {
        userData = await response.json();
      } catch (error) {
        console.error('Erro ao processar resposta JSON:', error);
        throw new Error('Resposta inválida do servidor');
      }
      
      if (response.ok) {
        setUser(userData);
        setToken(token);
      } else {
        // Se a requisição falhar, limpar o token
        console.error('Falha na autenticação:', userData);
        localStorage.removeItem('token');
      }
    } catch (error) {
      console.error('Erro ao buscar dados do usuário:', error);
      localStorage.removeItem('token');
    } finally {
      setIsLoading(false);
    }
  };
  
  const login = (token: string, userData: any) => {
    localStorage.setItem('token', token);
    setToken(token);
    setUser(userData);
    
    // Também podemos definir um cookie para o middleware
    document.cookie = `token=${token}; path=/; max-age=${60 * 60 * 24 * 7}`; // 7 dias
  };
  
  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    
    // Remover o cookie
    document.cookie = 'token=; path=/; max-age=0';
    
    // Redirecionar para a página de login
    window.location.href = '/login';
  };
  
  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

// Hook para usar o contexto de autenticação
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
}

// Componente do botão de logout
export function LogoutButton() {
  const { logout } = useAuth();
  
  return (
    <button 
      onClick={logout}
      className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded"
    >
      Sair
    </button>
  );
}