'use client';

//app/login/page.tsx

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../contexts/auth-context';
import Link from 'next/link';

export default function LoginPage() {
  const { login, isLoading, user } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    // Corrigido: Obter 'email' em vez de 'username'
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;

    // Corrigido: Verificar 'email' em vez de 'username'
    if (!email || !password) {
      alert('Por favor, preencha todos os campos');
      return;
    }

    const apiUrl = process.env.NEXT_PUBLIC_API_URL;
    if (!apiUrl) {
        console.error("Erro Crítico: A variável de ambiente NEXT_PUBLIC_API_URL não está definida!");
        alert("Erro de configuração do sistema. Contate o administrador.");
        return;
    }
    const loginUrl = `${apiUrl}/auth/login`;
    console.log(`Enviando requisição de login para: ${loginUrl}`);

    try {
      const response = await fetch(loginUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // Corrigido: Enviar 'email' em vez de 'username'
        body: JSON.stringify({ email, password }),
      });

      console.log('Status da resposta:', response.status);

      let data;
      const responseText = await response.text();
      console.log('Texto da resposta:', responseText);

      try {
        if (responseText) {
          data = JSON.parse(responseText);
        } else {
           if (!response.ok) throw new Error('Resposta vazia do servidor com erro de status.');
           data = {};
        }
      } catch (error) {
        console.error('Erro ao processar resposta JSON:', error);
        throw new Error(`Resposta inválida do servidor (não JSON). Status: ${response.status}. Resposta: ${responseText}`);
      }

      if (!response.ok) {
        // Tentar extrair mensagem de erro do Pydantic (pode estar em data.detail[0].msg)
        let errorMessage = `Erro ao fazer login (Status: ${response.status})`;
        if (data?.detail && Array.isArray(data.detail) && data.detail[0]?.msg) {
            errorMessage = data.detail[0].msg;
        } else if (data?.detail) {
            errorMessage = data.detail;
        }
        throw new Error(errorMessage);
      }

      if (!data.access_token) {
          throw new Error("Token de acesso não encontrado na resposta do servidor.");
      }

      // Corrigido: Passar 'email' ou o objeto de usuário retornado
      login(data.access_token, data.user || { email });

      router.push('/dashboard');
    } catch (err: any) {
      console.error('Erro completo durante o login:', err);
      alert(err.message || 'Ocorreu um erro inesperado ao fazer login');
    }
  };

  useEffect(() => {
    if (user && !isLoading) {
      router.push('/dashboard');
    }
  }, [user, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
       <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
         <div className="text-center mb-8">
           <h1 className="text-3xl font-bold text-gray-800">PontoAgent</h1>
           <p className="text-gray-600 mt-2">Sistema de Gestão de Ponto</p>
         </div>
         <form onSubmit={handleSubmit} className="space-y-6">
           <div>
             {/* Corrigido: Label, id, name e placeholder para 'email' */}
             <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1"> E-mail </label>
             <input id="email" name="email" type="email" required autoComplete="email" className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Digite seu e-mail" />
           </div>
           <div>
             <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1"> Senha </label>
             <input id="password" name="password" type="password" required autoComplete="current-password" className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Digite sua senha" />
           </div>
            <div className="flex items-center justify-between">
             <div className="flex items-center">
               <input id="remember-me" name="remember-me" type="checkbox" className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
               <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700"> Lembrar-me </label>
             </div>
             <div className="text-sm">
               <Link href="/esqueci-minha-senha" className="text-blue-600 hover:text-blue-500">
                 Esqueceu a senha?
               </Link>
             </div>
           </div>
           <button type="submit" className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500" > Entrar </button>
         </form>
         <div className="mt-6 text-center text-sm text-gray-500">
           <p>© 2025 PontoAgent - Todos os direitos reservados</p>
         </div>
       </div>
    </div>
  );
}