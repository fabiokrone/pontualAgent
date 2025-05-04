'use client';

import { useState } from 'react';
import { useApi, authService } from '../../../services/api';

// Componente para exportação de relatório em CSV
export default function RelatorioCsvPage() {
  const { isLoading, setLoading, error, setError } = useApi();
  const [csvUrl, setCsvUrl] = useState<string | null>(null);
  const [reportConfig, setReportConfig] = useState({
    tipo: 'dados_brutos',
    incluirCabecalho: true,
    delimitador: ',',
    codificacao: 'UTF-8'
  });

  // Função para gerar CSV
  const generateCsv = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Simular geração de CSV
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Em um cenário real, receberíamos a URL do CSV gerado pela API
      // Por enquanto, vamos simular com uma URL estática
      setCsvUrl('/sample-report.csv');
    } catch (err) {
      console.error('Erro ao gerar CSV:', err);
      setError('Não foi possível gerar o relatório em CSV. Por favor, tente novamente mais tarde.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Relatório em CSV</h1>
          <p className="text-gray-600">Configure e gere relatórios em formato CSV para importação em outros sistemas</p>
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-medium text-gray-700 mb-4">Configurações do CSV</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="tipo" className="block text-sm font-medium text-gray-700 mb-1">
              Tipo de Dados
            </label>
            <select
              id="tipo"
              name="tipo"
              value={reportConfig.tipo}
              onChange={(e) => setReportConfig({ ...reportConfig, tipo: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="dados_brutos">Dados Brutos de Batidas</option>
              <option value="resumo_diario">Resumo Diário</option>
              <option value="resumo_mensal">Resumo Mensal</option>
              <option value="justificativas">Justificativas</option>
            </select>
          </div>
          
          <div>
            <label htmlFor="delimitador" className="block text-sm font-medium text-gray-700 mb-1">
              Delimitador
            </label>
            <select
              id="delimitador"
              name="delimitador"
              value={reportConfig.delimitador}
              onChange={(e) => setReportConfig({ ...reportConfig, delimitador: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value=",">Vírgula (,)</option>
              <option value=";">Ponto e vírgula (;)</option>
              <option value="|">Pipe (|)</option>
              <option value="\t">Tab</option>
            </select>
          </div>
          
          <div>
            <label htmlFor="codificacao" className="block text-sm font-medium text-gray-700 mb-1">
              Codificação
            </label>
            <select
              id="codificacao"
              name="codificacao"
              value={reportConfig.codificacao}
              onChange={(e) => setReportConfig({ ...reportConfig, codificacao: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="UTF-8">UTF-8</option>
              <option value="ISO-8859-1">ISO-8859-1 (Latin1)</option>
              <option value="windows-1252">Windows-1252</option>
            </select>
          </div>
          
          <div className="flex items-center">
            <input
              id="incluirCabecalho"
              name="incluirCabecalho"
              type="checkbox"
              checked={reportConfig.incluirCabecalho}
              onChange={(e) => setReportConfig({ ...reportConfig, incluirCabecalho: e.target.checked })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="incluirCabecalho" className="ml-2 block text-sm text-gray-700">
              Incluir linha de cabeçalho
            </label>
          </div>
        </div>
        
        <div className="mt-6 flex justify-end">
          <button
            onClick={generateCsv}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {isLoading ? 'Gerando CSV...' : 'Gerar CSV'}
          </button>
        </div>
      </div>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Erro! </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}
      
      {csvUrl && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-medium text-gray-800 mb-4">Download do CSV</h3>
          <div className="border border-gray-300 rounded-lg overflow-hidden">
            <div className="bg-gray-100 p-4 flex justify-between items-center">
              <span className="text-gray-700 font-medium">Relatório gerado com sucesso</span>
              <a 
                href={csvUrl} 
                download="relatorio-ponto.csv"
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                Baixar CSV
              </a>
            </div>
            <div className="h-64 flex items-center justify-center bg-gray-50">
              <div className="text-center">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">Relatório CSV</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Clique no botão acima para baixar o relatório em formato CSV.
                </p>
                <p className="mt-1 text-sm text-gray-500">
                  Configurações: {reportConfig.incluirCabecalho ? 'Com cabeçalho' : 'Sem cabeçalho'}, 
                  Delimitador: {reportConfig.delimitador === ',' ? 'Vírgula' : 
                               reportConfig.delimitador === ';' ? 'Ponto e vírgula' : 
                               reportConfig.delimitador === '|' ? 'Pipe' : 'Tab'}, 
                  Codificação: {reportConfig.codificacao}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
