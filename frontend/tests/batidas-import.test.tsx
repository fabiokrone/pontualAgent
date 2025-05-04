import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import BatidasImportPage from '../app/dashboard/batidas/importar/page';
import { AuthProvider } from '../app/contexts/auth-context';
import { ApiProvider } from '../app/services/api';

// Mock do useRouter
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    back: jest.fn(),
  }),
}));

// Mock do FileReader
class MockFileReader {
  onload: any;
  readAsText(file: File) {
    this.onload({ target: { result: '000001|00003347|000001|01082024|0740|1|1|000001\n000001|00003347|000001|01082024|1153|1|1|000001' } });
  }
}

global.FileReader = MockFileReader as any;

describe('BatidasImportPage', () => {
  beforeEach(() => {
    render(
      <ApiProvider>
        <AuthProvider>
          <BatidasImportPage />
        </AuthProvider>
      </ApiProvider>
    );
  });

  it('renderiza a página de importação corretamente', () => {
    expect(screen.getByText('Importar Batidas')).toBeInTheDocument();
    expect(screen.getByText('Faça upload de um arquivo de batidas para processamento')).toBeInTheDocument();
    expect(screen.getByText('Clique para selecionar')).toBeInTheDocument();
    expect(screen.getByText('Instruções')).toBeInTheDocument();
  });

  it('exibe preview quando arquivo é selecionado', async () => {
    const file = new File(['dummy content'], 'batidas.txt', { type: 'text/plain' });
    const input = screen.getByLabelText(/Clique para selecionar/i);
    
    Object.defineProperty(input, 'files', {
      value: [file]
    });
    
    fireEvent.change(input);
    
    await waitFor(() => {
      expect(screen.getByText('Preview do Arquivo')).toBeInTheDocument();
    });
  });

  it('exibe erro quando arquivo inválido é selecionado', async () => {
    const file = new File(['dummy content'], 'batidas.pdf', { type: 'application/pdf' });
    const input = screen.getByLabelText(/Clique para selecionar/i);
    
    Object.defineProperty(input, 'files', {
      value: [file]
    });
    
    fireEvent.change(input);
    
    await waitFor(() => {
      expect(screen.getByText('Por favor, selecione um arquivo de texto (.txt)')).toBeInTheDocument();
    });
  });

  it('tenta enviar o formulário quando botão é clicado', async () => {
    // Mock da função fetch para simular upload
    global.fetch = jest.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({ total_batidas: 10 }),
    });

    const file = new File(['dummy content'], 'batidas.txt', { type: 'text/plain' });
    const input = screen.getByLabelText(/Clique para selecionar/i);
    
    Object.defineProperty(input, 'files', {
      value: [file]
    });
    
    fireEvent.change(input);
    
    await waitFor(() => {
      expect(screen.getByText('Preview do Arquivo')).toBeInTheDocument();
    });
    
    const submitButton = screen.getByRole('button', { name: /Importar Batidas/i });
    fireEvent.click(submitButton);
    
    // Verificar se a função fetch foi chamada
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });
  });
});
