
"use client"; // Necessário para usar hooks como useEffect, useRouter e useAuth

import { useEffect } from "react";
import { useRouter } from "next/navigation"; // Importar de next/navigation no App Router
import { useAuth } from "./contexts/auth-context"; // Ajuste o caminho se necessário

export default function HomePage() {
  const router = useRouter();
  const { token, loading } = useAuth(); // Obter o token e o estado de carregamento do contexto de autenticação

  useEffect(() => {
    // Só executa o redirecionamento depois que o estado de autenticação for carregado
    if (!loading) {
      if (token) {
        // Se existe um token (usuário autenticado), redireciona para o dashboard
        console.log("Usuário autenticado, redirecionando para /dashboard...");
        router.replace("/dashboard"); 
      } else {
        // Se não existe um token (usuário não autenticado), redireciona para o login
        console.log("Usuário não autenticado, redirecionando para /login...");
        router.replace("/login");
      }
    }
  }, [token, loading, router]); // Dependências do useEffect

  // Enquanto o estado de autenticação está carregando ou o redirecionamento está acontecendo,
  // exibe uma mensagem simples ou um componente de loading.
  // Isso evita que a página padrão pisque rapidamente antes do redirect.
  return (
    <div className="flex items-center justify-center min-h-screen">
      <p>Carregando...</p> 
      {/* Você pode substituir por um spinner ou componente de loading mais elaborado */}
    </div>
  );
}

