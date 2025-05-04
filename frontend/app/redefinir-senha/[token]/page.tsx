'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';

export default function ResetPasswordPage() {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [token, setToken] = useState<string | null>(null);

  const params = useParams();
  const router = useRouter();

  // Extract token from URL parameters on component mount
  console.log("Token original da URL:", params?.token);
  useEffect(() => {
    if (params?.token) {
      // Ensure token is treated as a string
      const urlToken = Array.isArray(params.token) ? params.token[0] : params.token;
      
      // Decodificar o token da URL usando o mesmo método que é compatível com quote do backend
      const decodedToken = decodeURIComponent(urlToken);
      console.log("Token da URL:", urlToken);
      console.log("Token decodificado:", decodedToken);
      
      // Usar o token decodificado para o estado
      setToken(decodedToken);
    } else {
      setError('Token de redefinição não encontrado na URL.');
      console.error('Token não encontrado nos parâmetros da URL:', params);
    }
  }, [params]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');
    setError('');

    if (!token) {
      setError('Token de redefinição inválido ou ausente.');
      setIsLoading(false);
      return;
    }

    if (!password || !confirmPassword) {
      setError('Por favor, preencha ambos os campos de senha.');
      setIsLoading(false);
      return;
    }

    if (password !== confirmPassword) {
      setError('As senhas não coincidem.');
      setIsLoading(false);
      return;
    }

    // Password strength validation (example: minimum 8 characters)
    if (password.length < 8) {
      setError('A nova senha deve ter pelo menos 8 caracteres.');
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

    const resetUrl = `${apiUrl}/auth/reset-password`;
    console.log(`Enviando requisição de redefinição para: ${resetUrl}`);

    try {
      // Preparar e logar o corpo da requisição
      const requestBody = { 
        token: token, 
        nova_senha: password, 
        confirmacao_nova_senha: confirmPassword 
      };
      console.log('Corpo da requisição para o backend:', JSON.stringify(requestBody));

      const response = await fetch(resetUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      const data = await response.json();
      console.log('Resposta completa da API:', data);

      if (!response.ok) {
        console.error('Erro na resposta da API:', data?.detail || response.statusText);
        setError(data?.detail || 'Ocorreu um erro ao redefinir sua senha. O link pode ter expirado ou ser inválido.');
      } else {
        setMessage(data.message || 'Senha redefinida com sucesso! Você já pode fazer login com sua nova senha.');
        // Optionally redirect to login page after a short delay
        setTimeout(() => {
          router.push('/login');
        }, 3000); // Redirect after 3 seconds
      }

    } catch (err: any) {
      console.error('Erro ao redefinir senha:', err);
      setError('Ocorreu um erro ao processar sua solicitação. Tente novamente mais tarde.');
    }
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800">Redefinir Senha</h1>
          <p className="text-gray-600 mt-2">Crie uma nova senha para sua conta.</p>
        </div>

        {message && (
          <div className="mb-4 p-3 rounded bg-green-100 text-green-800 text-sm">
            {message}
            <p className="mt-2">Você será redirecionado para a página de login em breve...</p>
          </div>
        )}
        {error && (
          <div className="mb-4 p-3 rounded bg-red-100 text-red-800 text-sm">
            {error}
          </div>
        )}

        {/* Only show form if token is valid and no success message */} 
        {token && !message && (
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Nova Senha
              </label>
              <input
                id="password"
                name="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Digite sua nova senha"
                disabled={isLoading}
              />
            </div>
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                Confirmar Nova Senha
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={8}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Confirme sua nova senha"
                disabled={isLoading}
              />
            </div>

            <button
              type="submit"
              disabled={isLoading || !token}
              className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${isLoading || !token ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'}`}
            >
              {isLoading ? 'Redefinindo...' : 'Redefinir Senha'}
            </button>
          </form>
        )}

        {/* Show link to login if there's an error or no token */} 
        {(error || !token) && !message && (
          <div className="mt-6 text-center text-sm">
            <Link href="/login" className="text-blue-600 hover:text-blue-500">
              Voltar para o Login
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}