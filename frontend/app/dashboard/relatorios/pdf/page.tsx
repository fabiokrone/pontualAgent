'use client';

import { useState } from 'react';
import { useApi, authService } from '../../../services/api';

// Componente para visualização de relatório em PDF
export default function RelatorioPdfPage() {
  const { isLoading, setLoading, error, setError } = useApi();
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [reportConfig, setReportConfig] = useState({
    tipo: 'individual',
    formato: 'detalhado',
    incluirGraficos: true,
    incluirAssinaturas: true
  });

  // Função para gerar PDF
  const generatePdf = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Simular geração de PDF
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Em um cenário real, receberíamos a URL do PDF gerado pela API
      // Por enquanto, vamos simular com uma URL estática
      setPdfUrl('/sample-report.pdf');
    } catch (err) {
      console.error('Erro ao gerar PDF:', err);
      setError('Não foi possível gerar o relatório em PDF. Por favor, tente novamente mais tarde.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Relatório em PDF</h1>
          <p className="text-gray-600">Configure e gere relatórios em formato PDF</p>
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-medium text-gray-700 mb-4">Configurações do PDF</h3>
        
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
          
          <div>
            <label htmlFor="formato" className="block text-sm font-medium text-gray-700 mb-1">
              Formato do Relatório
            </label>
            <select
              id="formato"
              name="formato"
              value={reportConfig.formato}
              onChange={(e) => setReportConfig({ ...reportConfig, formato: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="resumido">Resumido</option>
              <option value="detalhado">Detalhado</option>
              <option value="completo">Completo com Anexos</option>
            </select>
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
              Incluir gráficos e visualizações
            </label>
          </div>
          
          <div className="flex items-center">
            <input
              id="incluirAssinaturas"
              name="incluirAssinaturas"
              type="checkbox"
              checked={reportConfig.incluirAssinaturas}
              onChange={(e) => setReportConfig({ ...reportConfig, incluirAssinaturas: e.target.checked })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="incluirAssinaturas" className="ml-2 block text-sm text-gray-700">
              Incluir espaços para assinaturas
            </label>
          </div>
        </div>
        
        <div className="mt-6 flex justify-end">
          <button
            onClick={generatePdf}
            disabled={isLoading}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {isLoading ? 'Gerando PDF...' : 'Gerar PDF'}
          </button>
        </div>
      </div>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Erro! </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}
      
      {pdfUrl && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-medium text-gray-800 mb-4">Visualização do PDF</h3>
          <div className="border border-gray-300 rounded-lg overflow-hidden">
            <div className="bg-gray-100 p-4 flex justify-between items-center">
              <span className="text-gray-700 font-medium">Relatório gerado com sucesso</span>
              <a 
                href={pdfUrl} 
                download="relatorio-ponto.pdf"
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                Baixar PDF
              </a>
            </div>
            <div className="h-96 flex items-center justify-center bg-gray-50">
              <div className="text-center">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">Relatório PDF</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Clique no botão acima para baixar o relatório em formato PDF.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
