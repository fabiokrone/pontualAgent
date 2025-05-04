'use client';
import './globals.css'; 
import { ReactNode } from 'react';
import { AuthProvider } from './contexts/auth-context';
import { ApiProvider } from './services/api';

export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body>
        <ApiProvider>
          <AuthProvider>
            {children}
          </AuthProvider>
        </ApiProvider>
      </body>
    </html>
  );
}




