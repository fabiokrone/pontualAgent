'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
 
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');
    setError('');

    if (!email) {
      setError('Por favor, informe seu endereço de e-mail.');
      setIsLoading(false);
      return;
    }

    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    if (!apiUrl) {
        console.error("Erro Crítico: A variável de ambiente NEXT_PUBLIC_API_URL não está definida!");
        setError("Erro de configuração do sistema. Contate o administrador.");
        setIsLoading(false);
        return;
    }

    // Atualizado para usar o endpoint correto que está configurado no backend
    const recoveryUrl = `/api/auth/forgot-password`;
    console.log(`Enviando requisição de recuperação para: ${recoveryUrl}`);

    try {
      const response = await fetch(recoveryUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (!response.ok) {
        // Mesmo em caso de erro vindo do backend (ex: validação), mostramos a msg padrão
        // O backend já retorna uma mensagem genérica para não expor emails
        console.error('Erro na resposta da API:', data?.detail || response.statusText);
        setMessage(data?.message || 'Se um usuário com este e-mail existir, um link para redefinição de senha será enviado.');
      } else {
        setMessage(data.message || 'Solicitação enviada com sucesso. Verifique seu e-mail.');
      }
      setEmail(''); // Limpar campo após sucesso ou erro tratado

    } catch (err: any) {
      console.error('Erro ao solicitar recuperação de senha:', err);
      // Em caso de erro de rede ou falha na comunicação, mostramos um erro genérico
      setError('Ocorreu um erro ao processar sua solicitação. Tente novamente mais tarde.');
    }
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800">Recuperar Senha</h1>
          <p className="text-gray-600 mt-2">Informe seu e-mail para receber o link de redefinição.</p>
        </div>

        {message && (
          <div className="mb-4 p-3 rounded bg-green-100 text-green-800 text-sm">
            {message}
            <p className="mt-1">Verifique também sua pasta de spam se não encontrar o email.</p>
          </div>
        )}
        {error && (
          <div className="mb-4 p-3 rounded bg-red-100 text-red-800 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              E-mail
            </label>
            <input
              id="email"
              name="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="seu.email@exemplo.com"
              disabled={isLoading}
              autoFocus
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${isLoading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'}`}
          >
            {isLoading ? 'Enviando...' : 'Enviar Link de Recuperação'}
          </button>
        </form>

        <div className="mt-6 text-center text-sm">
          <Link href="/login" className="text-blue-600 hover:text-blue-500">
            Voltar para o Login
          </Link>
        </div>
      </div>
    </div>
  );
}