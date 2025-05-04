import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import RelatorioPdfPage from '../app/dashboard/relatorios/pdf/page';
import RelatorioExcelPage from '../app/dashboard/relatorios/excel/page';
import RelatorioCsvPage from '../app/dashboard/relatorios/csv/page';
import { ApiProvider } from '../app/services/api';

// Mock do useRouter
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    back: jest.fn(),
  }),
}));

describe('Páginas de Exportação de Relatórios', () => {
  describe('RelatorioPdfPage', () => {
    beforeEach(() => {
      render(
        <ApiProvider>
          <RelatorioPdfPage />
        </ApiProvider>
      );
    });

    it('renderiza a página de exportação PDF corretamente', () => {
      expect(screen.getByText('Relatório em PDF')).toBeInTheDocument();
      expect(screen.getByText('Configure e gere relatórios em formato PDF')).toBeInTheDocument();
      expect(screen.getByText('Configurações do PDF')).toBeInTheDocument();
    });

    it('permite configurar opções de PDF', () => {
      const tipoSelect = screen.getByLabelText('Tipo de Relatório');
      const formatoSelect = screen.getByLabelText('Formato do Relatório');
      const incluirGraficosCheckbox = screen.getByLabelText('Incluir gráficos e visualizações');
      const incluirAssinaturasCheckbox = screen.getByLabelText('Incluir espaços para assinaturas');

      fireEvent.change(tipoSelect, { target: { value: 'departamento' } });
      fireEvent.change(formatoSelect, { target: { value: 'resumido' } });
      fireEvent.click(incluirGraficosCheckbox);
      
      expect(tipoSelect).toHaveValue('departamento');
      expect(formatoSelect).toHaveValue('resumido');
      expect(incluirGraficosCheckbox).not.toBeChecked();
      expect(incluirAssinaturasCheckbox).toBeChecked();
    });

    it('gera PDF quando o botão é clicado', async () => {
      const generateButton = screen.getByRole('button', { name: 'Gerar PDF' });
      
      fireEvent.click(generateButton);
      
      await waitFor(() => {
        expect(screen.getByText('Relatório gerado com sucesso')).toBeInTheDocument();
        expect(screen.getByRole('link', { name: 'Baixar PDF' })).toBeInTheDocument();
      });
    });
  });

  describe('RelatorioExcelPage', () => {
    beforeEach(() => {
      render(
        <ApiProvider>
          <RelatorioExcelPage />
        </ApiProvider>
      );
    });

    it('renderiza a página de exportação Excel corretamente', () => {
      expect(screen.getByText('Relatório em Excel')).toBeInTheDocument();
      expect(screen.getByText('Configure e gere relatórios em formato Excel')).toBeInTheDocument();
      expect(screen.getByText('Configurações do Excel')).toBeInTheDocument();
    });

    it('permite configurar opções de Excel', () => {
      const tipoSelect = screen.getByLabelText('Tipo de Relatório');
      const incluirFormulasCheckbox = screen.getByLabelText('Incluir fórmulas para cálculos dinâmicos');
      const formatarCelulasCheckbox = screen.getByLabelText('Formatar células (cores, bordas, etc.)');
      const incluirGraficosCheckbox = screen.getByLabelText('Incluir gráficos automáticos');

      fireEvent.change(tipoSelect, { target: { value: 'individual' } });
      fireEvent.click(incluirFormulasCheckbox);
      
      expect(tipoSelect).toHaveValue('individual');
      expect(incluirFormulasCheckbox).not.toBeChecked();
      expect(formatarCelulasCheckbox).toBeChecked();
      expect(incluirGraficosCheckbox).toBeChecked();
    });

    it('gera Excel quando o botão é clicado', async () => {
      const generateButton = screen.getByRole('button', { name: 'Gerar Excel' });
      
      fireEvent.click(generateButton);
      
      await waitFor(() => {
        expect(screen.getByText('Relatório gerado com sucesso')).toBeInTheDocument();
        expect(screen.getByRole('link', { name: 'Baixar Excel' })).toBeInTheDocument();
      });
    });
  });

  describe('RelatorioCsvPage', () => {
    beforeEach(() => {
      render(
        <ApiProvider>
          <RelatorioCsvPage />
        </ApiProvider>
      );
    });

    it('renderiza a página de exportação CSV corretamente', () => {
      expect(screen.getByText('Relatório em CSV')).toBeInTheDocument();
      expect(screen.getByText('Configure e gere relatórios em formato CSV para importação em outros sistemas')).toBeInTheDocument();
      expect(screen.getByText('Configurações do CSV')).toBeInTheDocument();
    });

    it('permite configurar opções de CSV', () => {
      const tipoSelect = screen.getByLabelText('Tipo de Dados');
      const delimitadorSelect = screen.getByLabelText('Delimitador');
      const codificacaoSelect = screen.getByLabelText('Codificação');
      const incluirCabecalhoCheckbox = screen.getByLabelText('Incluir linha de cabeçalho');

      fireEvent.change(tipoSelect, { target: { value: 'resumo_diario' } });
      fireEvent.change(delimitadorSelect, { target: { value: ';' } });
      fireEvent.change(codificacaoSelect, { target: { value: 'ISO-8859-1' } });
      fireEvent.click(incluirCabecalhoCheckbox);
      
      expect(tipoSelect).toHaveValue('resumo_diario');
      expect(delimitadorSelect).toHaveValue(';');
      expect(codificacaoSelect).toHaveValue('ISO-8859-1');
      expect(incluirCabecalhoCheckbox).not.toBeChecked();
    });

    it('gera CSV quando o botão é clicado', async () => {
      const generateButton = screen.getByRole('button', { name: 'Gerar CSV' });
      
      fireEvent.click(generateButton);
      
      await waitFor(() => {
        expect(screen.getByText('Relatório gerado com sucesso')).toBeInTheDocument();
        expect(screen.getByRole('link', { name: 'Baixar CSV' })).toBeInTheDocument();
      });
    });
  });
});
