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
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>PontoAgent</title>
      </head>
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