/** @type {import('next').NextConfig} */
const nextConfig = {
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
  
  // Configuração de proxy removendo a regra problemática
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://app:8000/api/:path*',
      }
      // Removida a regra que estava causando o problema:
      // {
      //   source: '/redefinir-senha/:token',
      //   destination: '/redefinir-senha/[token]',
      // }
    ];
  },
};

module.exports = nextConfig;