'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function BatidasListPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [batidas, setBatidas] = useState([
    { id: 1, servidor: 'João Silva', matricula: '00003347', data: '01/08/2024', hora: '07:40', tipo: 'Entrada', status: 'Regular' },
    { id: 2, servidor: 'João Silva', matricula: '00003347', data: '01/08/2024', hora: '11:53', tipo: 'Saída', status: 'Regular' },
    { id: 3, servidor: 'João Silva', matricula: '00003347', data: '01/08/2024', hora: '12:15', tipo: 'Entrada', status: 'Regular' },
    { id: 4, servidor: 'João Silva', matricula: '00003347', data: '01/08/2024', hora: '16:59', tipo: 'Saída', status: 'Regular' },
    { id: 5, servidor: 'Maria Oliveira', matricula: '00004521', data: '01/08/2024', hora: '08:05', tipo: 'Entrada', status: 'Regular' },
    { id: 6, servidor: 'Maria Oliveira', matricula: '00004521', data: '01/08/2024', hora: '12:00', tipo: 'Saída', status: 'Regular' },
    { id: 7, servidor: 'Maria Oliveira', matricula: '00004521', data: '01/08/2024', hora: '13:10', tipo: 'Entrada', status: 'Regular' },
    { id: 8, servidor: 'Maria Oliveira', matricula: '00004521', data: '01/08/2024', hora: '17:15', tipo: 'Saída', status: 'Regular' },
  ]);
  const [filtro, setFiltro] = useState({
    servidor: '',
    dataInicio: '',
    dataFim: '',
    status: ''
  });
  const router = useRouter();

  const handleFiltroChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFiltro(prev => ({ ...prev, [name]: value }));
  };

  const handleFiltrar = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Simulação de busca com delay
    setTimeout(() => {
      // Aqui seria feita a chamada à API com os filtros
      setIsLoading(false);
    }, 500);
  };

  const handleImportar = () => {
    router.push('/dashboard/batidas/importar');
  };

  const handleVisualizarPonto = (matricula: string) => {
    router.push(`/dashboard/ponto/visualizar?matricula=${matricula}`);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Batidas de Ponto</h1>
          <p className="text-gray-600">Visualize e gerencie as batidas de ponto dos servidores</p>
        </div>
        <button
          onClick={handleImportar}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Importar Batidas
        </button>
      </div>
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-medium text-gray-700 mb-4">Filtros</h3>
        <form onSubmit={handleFiltrar} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label htmlFor="servidor" className="block text-sm font-medium text-gray-700 mb-1">
              Servidor
            </label>
            <input
              type="text"
              id="servidor"
              name="servidor"
              value={filtro.servidor}
              onChange={handleFiltroChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Nome ou matrícula"
            />
          </div>
          
          <div>
            <label htmlFor="dataInicio" className="block text-sm font-medium text-gray-700 mb-1">
              Data Início
            </label>
            <input
              type="date"
              id="dataInicio"
              name="dataInicio"
              value={filtro.dataInicio}
              onChange={handleFiltroChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div>
            <label htmlFor="dataFim" className="block text-sm font-medium text-gray-700 mb-1">
              Data Fim
            </label>
            <input
              type="date"
              id="dataFim"
              name="dataFim"
              value={filtro.dataFim}
              onChange={handleFiltroChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              id="status"
              name="status"
              value={filtro.status}
              onChange={handleFiltroChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Todos</option>
              <option value="regular">Regular</option>
              <option value="irregular">Irregular</option>
              <option value="justificada">Justificada</option>
            </select>
          </div>
          
          <div className="md:col-span-2 lg:col-span-4 flex justify-end">
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
            >
              {isLoading ? 'Filtrando...' : 'Filtrar'}
            </button>
          </div>
        </form>
      </div>
      
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Servidor</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Matrícula</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Data</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hora</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {batidas.map((batida) => (
                <tr key={batida.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{batida.servidor}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{batida.matricula}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{batida.data}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{batida.hora}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{batida.tipo}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      batida.status === 'Regular' ? 'bg-green-100 text-green-800' : 
                      batida.status === 'Irregular' ? 'bg-red-100 text-red-800' : 
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {batida.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <button
                      onClick={() => handleVisualizarPonto(batida.matricula)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Ver Ponto
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
          <div className="flex-1 flex justify-between sm:hidden">
            <a href="#" className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
              Anterior
            </a>
            <a href="#" className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
              Próximo
            </a>
          </div>
          <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                Mostrando <span className="font-medium">1</span> a <span className="font-medium">8</span> de <span className="font-medium">8</span> resultados
              </p>
            </div>
            <div>
              <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                <a href="#" className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50">
                  <span className="sr-only">Anterior</span>
                  <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </a>
                <a href="#" aria-current="page" className="z-10 bg-blue-50 border-blue-500 text-blue-600 relative inline-flex items-center px-4 py-2 border text-sm font-medium">
                  1
                </a>
                <a href="#" className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50">
                  <span className="sr-only">Próximo</span>
                  <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                  </svg>
                </a>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
