import Link from 'next/link';

export default function ResetPasswordIndex() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800">Redefinição de Senha</h1>
          <p className="text-gray-600 mt-2">
            Esta página é acessada através de um link enviado por e-mail.
          </p>
        </div>
        
        <div className="mb-4 p-3 rounded bg-yellow-100 text-yellow-800 text-sm">
          Se você precisa redefinir sua senha, solicite um novo link na página de login.
        </div>
        
        <div className="mt-6 text-center text-sm">
          <Link href="/esqueci-minha-senha" className="text-blue-600 hover:text-blue-500 block mb-2">
            Solicitar novo link de redefinição
          </Link>
          <Link href="/login" className="text-blue-600 hover:text-blue-500">
            Voltar para o Login
          </Link>
        </div>
      </div>
    </div>
  );
}