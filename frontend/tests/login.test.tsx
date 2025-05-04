import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import LoginPage from '../app/login/page';
import { AuthProvider } from '../app/contexts/auth-context';
import { ApiProvider } from '../app/services/api';

// Mock do useRouter
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

// Mock do localStorage
const localStorageMock = (function() {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString();
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    }
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

describe('LoginPage', () => {
  beforeEach(() => {
    localStorageMock.clear();
    render(
      <ApiProvider>
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </ApiProvider>
    );
  });

  it('renderiza o formulário de login corretamente', () => {
    expect(screen.getByText('Entrar no Sistema')).toBeInTheDocument();
    expect(screen.getByLabelText('Usuário')).toBeInTheDocument();
    expect(screen.getByLabelText('Senha')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Entrar' })).toBeInTheDocument();
  });

  it('exibe erro quando campos estão vazios', async () => {
    const loginButton = screen.getByRole('button', { name: 'Entrar' });
    fireEvent.click(loginButton);
    
    await waitFor(() => {
      expect(screen.getByText('Usuário é obrigatório')).toBeInTheDocument();
      expect(screen.getByText('Senha é obrigatória')).toBeInTheDocument();
    });
  });

  it('preenche o formulário e tenta fazer login', async () => {
    // Mock da função de login
    global.fetch = jest.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({ token: 'fake-token', user: { username: 'admin' } }),
    });

    const usernameInput = screen.getByLabelText('Usuário');
    const passwordInput = screen.getByLabelText('Senha');
    const loginButton = screen.getByRole('button', { name: 'Entrar' });

    fireEvent.change(usernameInput, { target: { value: 'admin' } });
    fireEvent.change(passwordInput, { target: { value: 'password' } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });
  });

  it('exibe mensagem de erro quando login falha', async () => {
    // Mock da função de login com erro
    global.fetch = jest.fn().mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Credenciais inválidas' }),
    });

    const usernameInput = screen.getByLabelText('Usuário');
    const passwordInput = screen.getByLabelText('Senha');
    const loginButton = screen.getByRole('button', { name: 'Entrar' });

    fireEvent.change(usernameInput, { target: { value: 'admin' } });
    fireEvent.change(passwordInput, { target: { value: 'wrong-password' } });
    fireEvent.click(loginButton);

    await waitFor(() => {
      expect(screen.getByText('Credenciais inválidas')).toBeInTheDocument();
    });
  });
});
