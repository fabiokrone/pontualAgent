import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import RelatoriosPage from '../app/dashboard/relatorios/page';
import { ApiProvider } from '../app/services/api';

// Mock do useRouter
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    back: jest.fn(),
  }),
}));

describe('RelatoriosPage', () => {
  beforeEach(() => {
    render(
      <ApiProvider>
        <RelatoriosPage />
      </ApiProvider>
    );
  });

  it('renderiza a página de relatórios corretamente', () => {
    expect(screen.getByText('Relatórios Avançados')).toBeInTheDocument();
    expect(screen.getByText('Gere relatórios personalizados com visualizações detalhadas')).toBeInTheDocument();
    expect(screen.getByText('Configurações do Relatório')).toBeInTheDocument();
  });

  it('permite selecionar período e tipo de relatório', () => {
    const startDateInput = screen.getByLabelText('Data Início');
    const endDateInput = screen.getByLabelText('Data Fim');
    const reportTypeSelect = screen.getByLabelText('Tipo de Relatório');

    fireEvent.change(startDateInput, { target: { value: '2025-04-01' } });
    fireEvent.change(endDateInput, { target: { value: '2025-04-30' } });
    fireEvent.change(reportTypeSelect, { target: { value: 'department' } });

    expect(startDateInput).toHaveValue('2025-04-01');
    expect(endDateInput).toHaveValue('2025-04-30');
    expect(reportTypeSelect).toHaveValue('department');
  });

  it('permite aplicar filtros adicionais', () => {
    const servidorInput = screen.getByLabelText('Servidor');
    const secretariaSelect = screen.getByLabelText('Secretaria');
    const statusSelect = screen.getByLabelText('Status');

    fireEvent.change(servidorInput, { target: { value: 'João Silva' } });
    fireEvent.change(secretariaSelect, { target: { value: 'administracao' } });
    fireEvent.change(statusSelect, { target: { value: 'regular' } });

    expect(servidorInput).toHaveValue('João Silva');
    expect(secretariaSelect).toHaveValue('administracao');
    expect(statusSelect).toHaveValue('regular');
  });

  it('gera relatório quando o botão é clicado', async () => {
    const generateButton = screen.getByRole('button', { name: 'Gerar Relatório' });
    
    fireEvent.click(generateButton);
    
    await waitFor(() => {
      expect(screen.getByText('Resultado do Relatório')).toBeInTheDocument();
      expect(screen.getByText('Exportar PDF')).toBeInTheDocument();
      expect(screen.getByText('Exportar Excel')).toBeInTheDocument();
      expect(screen.getByText('Exportar CSV')).toBeInTheDocument();
    });
  });

  it('exibe gráficos e tabelas após gerar relatório', async () => {
    const generateButton = screen.getByRole('button', { name: 'Gerar Relatório' });
    
    fireEvent.click(generateButton);
    
    await waitFor(() => {
      expect(screen.getByText('Horas Trabalhadas por Dia')).toBeInTheDocument();
      expect(screen.getByText('Distribuição de Status')).toBeInTheDocument();
      expect(screen.getByText('Resumo por Servidor')).toBeInTheDocument();
    });
  });

  it('permite exportar relatório em diferentes formatos', async () => {
    const generateButton = screen.getByRole('button', { name: 'Gerar Relatório' });
    
    fireEvent.click(generateButton);
    
    await waitFor(() => {
      const pdfButton = screen.getByRole('button', { name: 'Exportar PDF' });
      const excelButton = screen.getByRole('button', { name: 'Exportar Excel' });
      const csvButton = screen.getByRole('button', { name: 'Exportar CSV' });
      
      expect(pdfButton).toBeInTheDocument();
      expect(excelButton).toBeInTheDocument();
      expect(csvButton).toBeInTheDocument();
      
      // Simular alerta ao clicar no botão de exportação
      global.alert = jest.fn();
      
      fireEvent.click(pdfButton);
      expect(global.alert).toHaveBeenCalledWith(expect.stringContaining('PDF'));
      
      fireEvent.click(excelButton);
      expect(global.alert).toHaveBeenCalledWith(expect.stringContaining('EXCEL'));
      
      fireEvent.click(csvButton);
      expect(global.alert).toHaveBeenCalledWith(expect.stringContaining('CSV'));
    });
  });
});
