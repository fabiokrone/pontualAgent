'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function ImportBatidasPage() {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [previewData, setPreviewData] = useState<string[][]>([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const router = useRouter();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    // Verificar se é um arquivo de texto
    if (selectedFile.type !== 'text/plain' && !selectedFile.name.endsWith('.txt')) {
      setError('Por favor, selecione um arquivo de texto (.txt)');
      setFile(null);
      return;
    }

    setFile(selectedFile);
    setError('');
    
    // Ler o arquivo para preview
    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      const lines = content.split('\n').filter(line => line.trim() !== '');
      
      // Limitar a 10 linhas para o preview
      const previewLines = lines.slice(0, 10);
      
      // Processar cada linha para exibir em formato tabular
      const processedData = previewLines.map(line => {
        const parts = line.split('|');
        return parts;
      });
      
      setPreviewData(processedData);
    };
    
    reader.readAsText(selectedFile);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      setError('Por favor, selecione um arquivo para importar');
      return;
    }
    
    setIsUploading(true);
    setError('');
    setSuccess('');
    
    try {
      // Criar um FormData para enviar o arquivo
      const formData = new FormData();
      formData.append('file', file);
      
      // Enviar para a API
      const response = await fetch('http://localhost:8000/api/batidas/importar', {
        method: 'POST',
        body: formData,
        headers: {
          // Não incluir Content-Type aqui, o navegador vai definir automaticamente com o boundary correto
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Erro ao importar batidas');
      }
      
      setSuccess(`Arquivo importado com sucesso! ${data.total_batidas || 0} batidas processadas.`);
      
      // Limpar o arquivo e preview após sucesso
      setFile(null);
      setPreviewData([]);
      
      // Redirecionar após 2 segundos
      setTimeout(() => {
        router.push('/dashboard/batidas');
      }, 2000);
      
    } catch (err: any) {
      setError(err.message || 'Ocorreu um erro ao importar o arquivo');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Importar Batidas</h1>
          <p className="text-gray-600">Faça upload de um arquivo de batidas para processamento</p>
        </div>
        <button
          onClick={() => router.back()}
          className="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200"
        >
          Voltar
        </button>
      </div>
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          
          {success && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
              {success}
            </div>
          )}
          
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Arquivo de Batidas
            </label>
            <div className="flex items-center justify-center w-full">
              <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <svg className="w-10 h-10 mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p className="mb-2 text-sm text-gray-500">
                    <span className="font-semibold">Clique para selecionar</span> ou arraste e solte
                  </p>
                  <p className="text-xs text-gray-500">
                    Arquivo de texto (.txt) com formato específico
                  </p>
                </div>
                <input 
                  type="file" 
                  className="hidden" 
                  accept=".txt,text/plain" 
                  onChange={handleFileChange}
                  disabled={isUploading}
                />
              </label>
            </div>
            {file && (
              <p className="text-sm text-gray-500">
                Arquivo selecionado: <span className="font-medium">{file.name}</span> ({(file.size / 1024).toFixed(2)} KB)
              </p>
            )}
          </div>
          
          {previewData.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-lg font-medium text-gray-700">Preview do Arquivo</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Empresa</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Matrícula</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Local</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Data</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hora</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sentido</th>
                      <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Terminal</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {previewData.map((row, rowIndex) => (
                      <tr key={rowIndex}>
                        {row.map((cell, cellIndex) => (
                          <td key={cellIndex} className="px-3 py-2 whitespace-nowrap text-sm text-gray-500">
                            {cell}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="text-xs text-gray-500 italic">
                Mostrando {previewData.length} de {file?.size ? Math.ceil(file.size / 100) : '?'} linhas estimadas
              </p>
            </div>
          )}
          
          <div className="flex items-center justify-between pt-4">
            <div className="text-sm text-gray-500">
              <p>Formato esperado: empresa|matricula|local|data|hora|tipo|sentido|terminal</p>
              <p>Exemplo: 000001|00003347|000001|01082024|0740|1|1|000001</p>
            </div>
            <button
              type="submit"
              disabled={!file || isUploading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
            >
              {isUploading ? 'Importando...' : 'Importar Batidas'}
            </button>
          </div>
        </form>
      </div>
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-medium text-gray-700 mb-4">Instruções</h3>
        <div className="space-y-3 text-sm text-gray-600">
          <p>
            <span className="font-medium">1.</span> Prepare um arquivo de texto (.txt) com as batidas no formato especificado.
          </p>
          <p>
            <span className="font-medium">2.</span> Cada linha deve conter uma batida no formato: empresa|matricula|local|data|hora|tipo|sentido|terminal
          </p>
          <p>
            <span className="font-medium">3.</span> A data deve estar no formato DDMMAAAA e a hora no formato HHMM.
          </p>
          <p>
            <span className="font-medium">4.</span> Selecione o arquivo e clique em "Importar Batidas".
          </p>
          <p>
            <span className="font-medium">5.</span> Após a importação, as batidas serão processadas automaticamente.
          </p>
        </div>
      </div>
    </div>
  );
}
