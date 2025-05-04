import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Configurações existentes
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  reactStrictMode: true,
  
  // Configurações para melhorar o suporte a rotas dinâmicas
  trailingSlash: false,
  pageExtensions: ['ts', 'tsx', 'js', 'jsx'],
  
  // O App Router já é o padrão no Next.js 15+, então não precisamos mais de appDir
  // Mover serverComponentsExternalPackages para a raiz conforme recomendação dos warnings
  serverExternalPackages: [],
  
  // Configuração de proxy com adição da regra de reescrita para a rota dinâmica
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://app:8000/api/:path*',
      },
      // Regra específica para a rota de redefinição de senha
      {
        source: '/redefinir-senha/:token',
        destination: '/redefinir-senha/[token]',
      }
    ];
  },
};

export default nextConfig;