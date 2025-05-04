// Este arquivo define a configuração de geração de rotas dinâmicas
// Não precisa da diretiva 'use client' pois é um componente do servidor

import { ReactNode } from 'react';

export const dynamicParams = true;

// Forçar a geração de pelo menos uma rota dinâmica
export function generateStaticParams() {
  return [{ token: 'placeholder' }];
}

// O layout simplesmente passa os children sem modificação
export default function ResetPasswordTokenLayout({
  children,
}: {
  children: ReactNode;
}) {
  // Este layout não altera a estrutura, apenas configura a rota
  return children;
}