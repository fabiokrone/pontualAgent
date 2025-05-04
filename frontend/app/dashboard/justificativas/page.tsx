'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function JustificativasPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [justificativas, setJustificativas] = useState<any[]>([]);
  const [filtro, setFiltro] = useState({
    servidor: '',
    dataInicio: '',
    dataFim: '',
    status: '',
    tipo: ''
  });

  useEffect(() => {
    // Função para buscar justificativas
    const fetchJustificativas = async () => {
      try {
        setIsLoading(true);
        
        // Em um cenário real, buscaríamos esses dados da API
        // Por enquanto, vamos simular com dados estáticos
        
        // Simular uma chamada de API
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Dados simulados
        const justificativasSimuladas = [
          {
            id: 1,
            servidor: 'João Silva',
            matricula: '00003347',
            data: '27/04/2025',
            tipo: 'Atestado Médico',
            descricao: 'Consulta médica no período da tarde',
            status: 'Pendente',
            dataEnvio: '26/04/2025',
            anexo: true
          },
          {
            id: 2,
            servidor: 'Maria Oliveira',
            matricula: '00004521',
            data: '26/04/2025',
            tipo: 'Declaração de Comparecimento',
            descricao: 'Comparecimento em reunião escolar do filho',
            status: 'Aprovada',
            dataEnvio: '24/04/2025',
            anexo: true
          },
          {
            id: 3,
            servidor: 'Carlos Santos',
            matricula: '00002189',
            data: '25/04/2025',
            tipo: 'Falta Abonada',
            descricao: 'Problemas pessoais',
            status: 'Rejeitada',
            dataEnvio: '24/04/2025',
            anexo: false
          },
          {
            id: 4,
            servidor: 'Ana Pereira',
            matricula: '00005632',
            data: '24/04/2025',
            tipo: 'Atestado Médico',
            descricao: 'Atestado médico para o dia inteiro',
            status: 'Aprovada',
            dataEnvio: '23/04/2025',
            anexo: true
          },
          {
            id: 5,
            servidor: 'Pedro Souza',
            matricula: '00001478',
            data: '23/04/2025',
            tipo: 'Declaração de Comparecimento',
            descricao: 'Comparecimento em órgão público',
            status: 'Pendente',
            dataEnvio: '22/04/2025',
            anexo: true
          }
        ];
        
        setJustificativas(justificativasSimuladas);
      } catch (error) {
        console.error('Erro ao buscar justificativas:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchJustificativas();
  }, []);

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

  const handleAprovar = async (id: number) => {
    try {
      // Simulação de aprovação
      setJustificativas(prev => 
        prev.map(j => j.id === id ? { ...j, status: 'Aprovada' } : j)
      );
      
      // Aqui seria feita a chamada à API para aprovar a justificativa
      alert(`Justificativa #${id} aprovada com sucesso!`);
    } catch (error) {
      console.error('Erro ao aprovar justificativa:', error);
      alert('Erro ao aprovar justificativa');
    }
  };

  const handleRejeitar = async (id: number) => {
    try {
      // Simulação de rejeição
      setJustificativas(prev => 
        prev.map(j => j.id === id ? { ...j, status: 'Rejeitada' } : j)
      );
      
      // Aqui seria feita a chamada à API para rejeitar a justificativa
      alert(`Justificativa #${id} rejeitada com sucesso!`);
    } catch (error) {
      console.error('Erro ao rejeitar justificativa:', error);
      alert('Erro ao rejeitar justificativa');
    }
  };

  const handleVerAnexo = (id: number) => {
    // Em um cenário real, abriríamos o anexo
    alert(`Visualizando anexo da justificativa #${id}`);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Justificativas</h1>
          <p className="text-gray-600">Gerencie as justificativas de ausência e irregularidades</p>
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-medium text-gray-700 mb-4">Filtros</h3>
        <form onSubmit={handleFiltrar} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
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
              <option value="pendente">Pendente</option>
              <option value="aprovada">Aprovada</option>
              <option value="rejeitada">Rejeitada</option>
            </select>
          </div>
          
          <div>
            <label htmlFor="tipo" className="block text-sm font-medium text-gray-700 mb-1">
              Tipo
            </label>
            <select
              id="tipo"
              name="tipo"
              value={filtro.tipo}
              onChange={handleFiltroChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Todos</option>
              <option value="atestado">Atestado Médico</option>
              <option value="declaracao">Declaração de Comparecimento</option>
              <option value="falta">Falta Abonada</option>
              <option value="outro">Outro</option>
            </select>
          </div>
          
          <div className="md:col-span-2 lg:col-span-5 flex justify-end">
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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descrição</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-4 text-center">
                    <div className="flex justify-center">
                      <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-blue-500"></div>
                    </div>
                  </td>
                </tr>
              ) : justificativas.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-4 text-center text-gray-500">
                    Nenhuma justificativa encontrada
                  </td>
                </tr>
              ) : (
                justificativas.map((justificativa) => (
                  <tr key={justificativa.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{justificativa.servidor}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{justificativa.matricula}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{justificativa.data}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{justificativa.tipo}</td>
                    <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">{justificativa.descricao}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        justificativa.status === 'Aprovada' ? 'bg-green-100 text-green-800' : 
                        justificativa.status === 'Rejeitada' ? 'bg-red-100 text-red-800' : 
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {justificativa.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex space-x-2">
                        {justificativa.status === 'Pendente' && (
                          <>
                            <button
                              onClick={() => handleAprovar(justificativa.id)}
                              className="text-green-600 hover:text-green-900"
                            >
                              Aprovar
                            </button>
                            <button
                              onClick={() => handleRejeitar(justificativa.id)}
                              className="text-red-600 hover:text-red-900"
                            >
                              Rejeitar
                            </button>
                          </>
                        )}
                        {justificativa.anexo && (
                          <button
                            onClick={() => handleVerAnexo(justificativa.id)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            Ver Anexo
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
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
                Mostrando <span className="font-medium">1</span> a <span className="font-medium">{justificativas.length}</span> de <span className="font-medium">{justificativas.length}</span> resultados
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
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-medium text-gray-700 mb-4">Detalhes da Aprovação</h3>
        <div className="space-y-4">
          <p className="text-gray-600">
            Ao aprovar uma justificativa, você está confirmando que a ausência ou irregularidade no ponto do servidor está devidamente justificada e não deve ser considerada como falta ou atraso.
          </p>
          <p className="text-gray-600">
            Ao rejeitar uma justificativa, o servidor será notificado e a irregularidade permanecerá em seu registro de ponto.
          </p>
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-yellow-700">
                  Lembre-se de verificar cuidadosamente os anexos e a descrição antes de aprovar ou rejeitar uma justificativa.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
