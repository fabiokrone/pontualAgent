'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '../contexts/auth-context';

// Componente de Sidebar
const Sidebar = ({ isOpen, toggleSidebar }: { isOpen: boolean, toggleSidebar: () => void }) => {
  const { logout } = useAuth();
  
  return (
    <div className={`fixed inset-y-0 left-0 z-30 w-64 bg-gray-800 text-white transform ${isOpen ? 'translate-x-0' : '-translate-x-full'} transition-transform duration-300 ease-in-out md:translate-x-0`}>
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        <h1 className="text-xl font-bold">PontoAgent</h1>
        <button onClick={toggleSidebar} className="md:hidden text-white">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <nav className="mt-4">
        <ul>
          <li>
            <Link href="/dashboard" className="block px-4 py-2 text-gray-300 hover:bg-gray-700 hover:text-white">
              Dashboard
            </Link>
          </li>
          <li>
            <Link href="/dashboard/servidores" className="block px-4 py-2 text-gray-300 hover:bg-gray-700 hover:text-white">
              Servidores
            </Link>
          </li>
          <li>
            <Link href="/dashboard/batidas" className="block px-4 py-2 text-gray-300 hover:bg-gray-700 hover:text-white">
              Batidas
            </Link>
          </li>
          <li>
            <Link href="/dashboard/justificativas" className="block px-4 py-2 text-gray-300 hover:bg-gray-700 hover:text-white">
              Justificativas
            </Link>
          </li>
          <li>
            <Link href="/dashboard/relatorios" className="block px-4 py-2 text-gray-300 hover:bg-gray-700 hover:text-white">
              Relatórios
            </Link>
          </li>
        </ul>
      </nav>
      
      <div className="absolute bottom-0 w-full p-4 border-t border-gray-700">
        <button 
          onClick={logout}
          className="w-full px-4 py-2 text-white bg-red-600 hover:bg-red-700 rounded"
        >
          Sair
        </button>
      </div>
    </div>
  );
};

// Componente de Header
const Header = ({ toggleSidebar }: { toggleSidebar: () => void }) => {
  const { user } = useAuth();
  
  return (
    <header className="bg-white shadow-md">
      <div className="flex items-center justify-between px-4 py-3">
        <button onClick={toggleSidebar} className="md:hidden text-gray-600">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        
        <div className="flex items-center space-x-4">
          <div className="relative">
            <button className="flex items-center space-x-2 text-gray-700 hover:text-gray-900">
              <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium">{user?.username?.charAt(0).toUpperCase() || 'U'}</span>
              </div>
              <span className="hidden md:inline-block">{user?.username || 'Usuário'}</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

// Layout do Dashboard
export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };
  
  return (
    <div className="min-h-screen bg-gray-100">
      <Sidebar isOpen={sidebarOpen} toggleSidebar={toggleSidebar} />
      
      <div className="md:ml-64 flex flex-col min-h-screen">
        <Header toggleSidebar={toggleSidebar} />
        
        <main className="flex-grow p-4">
          {children}
        </main>
        
        <footer className="bg-white p-4 text-center text-gray-600 text-sm">
          © 2025 PontoAgent - Todos os direitos reservados
        </footer>
      </div>
      
      {/* Overlay para fechar o sidebar em dispositivos móveis */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-20 md:hidden"
          onClick={toggleSidebar}
        />
      )}
    </div>
  );
}
