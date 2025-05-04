import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Rotas que não precisam de autenticação
const publicRoutes = ['/login', '/forgot-password', '/esqueci-minha-senha', '/redefinir-senha'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Verificar se a rota atual é pública, incluindo rotas com parâmetros dinâmicos
  const isPublicRoute = publicRoutes.some(route => 
    pathname === route || pathname.startsWith(`${route}/`)
  );
  
  // Obter o token do localStorage (cookies no servidor)
  const token = request.cookies.get('token')?.value;
  
  // Se não for uma rota pública e não tiver token, redirecionar para login
  if (!isPublicRoute && !token) {
    const url = new URL('/login', request.url);
    url.searchParams.set('from', pathname);
    return NextResponse.redirect(url);
  }
  
  // Se for a rota de login e tiver token, redirecionar para dashboard
  if (pathname === '/login' && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }
  
  return NextResponse.next();
}

// Configurar em quais caminhos o middleware deve ser executado
export const config = {
  matcher: [
    // Adicionar matcher específico para a rota de redefinição de senha com token
    '/redefinir-senha/:path*',
    // Matcher genérico para outras rotas
    '/((?!api|_next|fonts|images|favicon.ico|logo.png).*)',
  ],
};