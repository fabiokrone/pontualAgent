"use client";

import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Interface para tipar os dados do servidor (baseado no schema ou modelo)
interface Servidor {
  id: number;
  nome: string;
  matricula: string;
  cpf: string;
  email: string | null;
  ativo: boolean;
  secretaria_id: number | null;
  // Adicione outros campos se necessário, conforme o schema ServidorInDB
}

const ServidoresPage = () => {
  const [servidores, setServidores] = useState<Servidor[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchServidores = async () => {
      setLoading(true);
      setError(null);
      // Determina a URL da API baseada no ambiente (Docker vs. local)
      // Usar NEXT_PUBLIC_API_DOCKER_URL se disponível (dentro do Docker), senão NEXT_PUBLIC_API_URL
      const apiUrl = process.env.NEXT_PUBLIC_API_DOCKER_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'; 
      
      try {
        // Ajuste o endpoint conforme a estrutura da sua API (incluindo /api)
        const response = await axios.get(`${apiUrl}/api/servidores`); 
        setServidores(response.data);
      } catch (err) {
        console.error("Erro ao buscar servidores:", err);
        setError('Falha ao carregar os dados dos servidores. Tente novamente mais tarde.');
      } finally {
        setLoading(false);
      }
    };

    fetchServidores();
  }, []);

  if (loading) {
    // Idealmente, usar um componente de loading consistente com o resto do dashboard
    return <p>Carregando servidores...</p>; 
  }

  if (error) {
    // Idealmente, usar um componente de erro consistente
    return <p className="text-red-500">{error}</p>; 
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-4">Gerenciamento de Servidores</h1>
      
      {/* Tabela para exibir os servidores - Estilizar conforme o padrão do dashboard */}
      <div className="overflow-x-auto shadow-md sm:rounded-lg">
        <table className="min-w-full text-sm text-left text-gray-500 dark:text-gray-400">
          <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
            <tr>
              <th scope="col" className="px-6 py-3">Nome</th>
              <th scope="col" className="px-6 py-3">Matrícula</th>
              <th scope="col" className="px-6 py-3">CPF</th>
              <th scope="col" className="px-6 py-3">Email</th>
              <th scope="col" className="px-6 py-3">Status</th>
              {/* Adicionar coluna de Ações se necessário */}
            </tr>
          </thead>
          <tbody>
            {servidores.length > 0 ? (
              servidores.map((servidor) => (
                <tr key={servidor.id} className="bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600">
                  <td className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">{servidor.nome}</td>
                  <td className="px-6 py-4">{servidor.matricula}</td>
                  <td className="px-6 py-4">{servidor.cpf}</td>
                  <td className="px-6 py-4">{servidor.email || '-'}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${servidor.ativo ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'}`}>
                      {servidor.ativo ? 'Ativo' : 'Inativo'}
                    </span>
                  </td>
                  {/* Adicionar célula de Ações se necessário */}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5} className="px-6 py-4 text-center">Nenhum servidor encontrado.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ServidoresPage;
