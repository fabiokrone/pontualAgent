'use client';

import { useState } from 'react';
import { useApi, authService } from '../../../services/api';


// Componente para exportação de relatório em Excel
export default function RelatorioExcelPage() {
  const { isLoading, setLoading, error, setError } = useApi();
  const [excelUrl, setExcelUrl] = useState<string | null>(null);
  const [reportConfig, setReportConfig] = useState({
    tipo: 'consolidado',
    incluirFormulas: true,
    formatarCelulas: true,
    incluirGraficos: true
  });

  // Função para gerar Excel
  const generateExcel = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Simular geração de Excel
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Em um cenário real, receberíamos a URL do Excel gerado pela API
      // Por enquanto, vamos simular com uma URL estática
      setExcelUrl('/sample-report.xlsx');
    } catch (err) {
      console.error('Erro ao gerar Excel:', err);
      setError('Não foi possível gerar o relatório em Excel. Por favor, tente novamente mais tarde.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Relatório em Excel</h1>
          <p className="text-gray-600">Configure e gere relatórios em formato Excel</p>
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-medium text-gray-700 mb-4">Configurações do Excel</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="tipo" className="block text-sm font-medium text-gray-700 mb-1">
              Tipo de Relatório
            </label>
            <select
              id="tipo"
              name="tipo"
              value={reportConfig.tipo}
              onChange={(e) => setReportConfig({ ...reportConfig, tipo: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="individual">Individual por Servidor</option>
              <option value="departamento">Por Departamento</option>
              <option value="consolidado">Consolidado</option>
            </select>
          </div>
          
          <div className="flex items-center">
            <input
              id="incluirFormulas"
              name="incluirFormulas"
              type="checkbox"
              checked={reportConfig.incluirFormulas}
              onChange={(e) => setReportConfig({ ...reportConfig, incluirFormulas: e.target.checked })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="incluirFormulas" className="ml-2 block text-sm text-gray-700">
              Incluir fórmulas para cálculos dinâmicos
            </label>
          </div>
          
          <div className="flex items-center">
            <input
              id="formatarCelulas"
              name="formatarCelulas"
              type="checkbox"
              checked={reportConfig.formatarCelulas}
              onChange={(e) => setReportConfig({ ...reportConfig, formatarCelulas: e.target.checked })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="formatarCelulas" className="ml-2 block text-sm text-gray-700">
              Formatar células (cores, bordas, etc.)
            </label>
          </div>
          
          <div className="flex items-center">
            <input
              id="incluirGraficos"
              name="incluirGraficos"
              type="checkbox"
              checked={reportConfig.incluirGraficos}
              onChange={(e) => setReportConfig({ ...reportConfig, incluirGraficos: e.target.checked })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="incluirGraficos" className="ml-2 block text-sm text-gray-700">
              Incluir gráficos automáticos
            </label>
          </div>
        </div>
        
        <div className="mt-6 flex justify-end">
          <button
            onClick={generateExcel}
            disabled={isLoading}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {isLoading ? 'Gerando Excel...' : 'Gerar Excel'}
          </button>
        </div>
      </div>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Erro! </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}
      
      {excelUrl && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-medium text-gray-800 mb-4">Download do Excel</h3>
          <div className="border border-gray-300 rounded-lg overflow-hidden">
            <div className="bg-gray-100 p-4 flex justify-between items-center">
              <span className="text-gray-700 font-medium">Relatório gerado com sucesso</span>
              <a 
                href={excelUrl} 
                download="relatorio-ponto.xlsx"
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
              >
                Baixar Excel
              </a>
            </div>
            <div className="h-64 flex items-center justify-center bg-gray-50">
              <div className="text-center">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">Relatório Excel</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Clique no botão acima para baixar o relatório em formato Excel.
                </p>
                <p className="mt-1 text-sm text-gray-500">
                  O arquivo contém todas as configurações solicitadas.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
