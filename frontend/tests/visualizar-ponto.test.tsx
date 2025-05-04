import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import VisualizarPontoPage from '../app/dashboard/ponto/visualizar/page';
import { AuthProvider } from '../app/contexts/auth-context';
import { ApiProvider } from '../app/services/api';

// Mock do useRouter e useSearchParams
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    back: jest.fn(),
  }),
  useSearchParams: () => ({
    get: jest.fn().mockImplementation((param) => {
      if (param === 'matricula') return '00003347';
      return null;
    }),
  }),
}));

// Mock do window.print
global.print = jest.fn();
Object.defineProperty(window, 'print', {
  value: jest.fn(),
});

describe('VisualizarPontoPage', () => {
  beforeEach(() => {
    // Mock da função fetch para simular dados do espelho de ponto
    global.fetch = jest.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        servidor: {
          nome: 'João Silva',
          matricula: '00003347',
          cargo: 'Analista Administrativo',
          secretaria: 'Secretaria de Administração',
        },
        resumo: {
          totalDias: 30,
          diasTrabalhados: 22,
          horasTrabalhadas: '176:00',
          horasExtras: '8:00',
          horasFaltantes: '0:00',
          diasJustificados: 0,
        },
        espelho: [
          {
            data: '01/04/2025',
            diaSemana: 'Terça',
            batidas: [
              { hora: '08:00', tipo: 'Entrada' },
              { hora: '12:00', tipo: 'Saída' },
              { hora: '13:00', tipo: 'Entrada' },
              { hora: '17:00', tipo: 'Saída' },
            ],
            horasTrabalhadas: '8:00',
            horasExtras: '0:00',
            horasFaltantes: '0:00',
            status: 'Regular',
            observacao: '',
          },
        ],
      }),
    });

    render(
      <ApiProvider>
        <AuthProvider>
          <VisualizarPontoPage />
        </AuthProvider>
      </ApiProvider>
    );
  });

  it('renderiza a página de visualização de ponto corretamente', async () => {
    await waitFor(() => {
      expect(screen.getByText('Espelho de Ponto')).toBeInTheDocument();
      expect(screen.getByText('Dados do Servidor')).toBeInTheDocument();
      expect(screen.getByText('Resumo do Período')).toBeInTheDocument();
      expect(screen.getByText('Detalhamento Diário')).toBeInTheDocument();
    });
  });

  it('exibe os dados do servidor corretamente', async () => {
    await waitFor(() => {
      expect(screen.getByText('João Silva')).toBeInTheDocument();
      expect(screen.getByText('00003347')).toBeInTheDocument();
      expect(screen.getByText('Analista Administrativo')).toBeInTheDocument();
      expect(screen.getByText('Secretaria de Administração')).toBeInTheDocument();
    });
  });

  it('exibe o resumo do período corretamente', async () => {
    await waitFor(() => {
      expect(screen.getByText('22 / 22')).toBeInTheDocument(); // Dias trabalhados
      expect(screen.getByText('176:00')).toBeInTheDocument(); // Horas trabalhadas
      expect(screen.getByText('8:00')).toBeInTheDocument(); // Horas extras
    });
  });

  it('permite mudar o período', async () => {
    const periodoInput = screen.getByLabelText('Selecione o Período');
    fireEvent.change(periodoInput, { target: { value: '2025-03' } });
    
    // Verificar se a função fetch foi chamada novamente com o novo período
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });
  });

  it('chama a função de impressão quando o botão é clicado', async () => {
    await waitFor(() => {
      const imprimirButton = screen.getByRole('button', { name: 'Imprimir' });
      fireEvent.click(imprimirButton);
      expect(window.print).toHaveBeenCalled();
    });
  });
});
