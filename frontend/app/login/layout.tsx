'use client';
// app/login/layout.tsx

import { ReactNode } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import Image from 'next/image';

interface AuthLayoutProps {
  children: ReactNode;
}

export default function AuthLayout({ children }: AuthLayoutProps) {
  const pathname = usePathname();
  
  // Verificar se estamos em uma página de autenticação
  const isAuthPage = pathname === '/login' || pathname === '/esqueci-minha-senha' || pathname === '/redefinir-senha';
  
  if (!isAuthPage) {
    return <>{children}</>;
  }
  
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto px-4 py-8">
        {children}
      </div>
    </div>
  );
}
