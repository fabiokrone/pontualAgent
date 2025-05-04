'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useApi, authService } from '../../services/api';

// ======= INTERFACES =======

// Interface para o período
interface Period {
  startDate: string;
  endDate: string;
  reportType: string;
}

// Interface para as props do componente PeriodSelector
interface PeriodSelectorProps {
  period: Period;
  setPeriod: React.Dispatch<React.SetStateAction<Period>>;
}

// Interface para filtros
interface Filters {
  servidor: string;
  secretaria: string;
  status: string;
}

// Interface para as props do componente AdditionalFilters
interface AdditionalFiltersProps {
  filters: Filters;
  setFilters: React.Dispatch<React.SetStateAction<Filters>>;
}

// Interface para as props do componente ExportOptions
interface ExportOptionsProps {
  onExport: (format: string) => void;
}

// Interface para os dados do dia no WorkHoursChart
interface DayData {
  date: string;
  hoursWorked: number;
}

// Interface para as props do componente WorkHoursChart
interface WorkHoursChartProps {
  data: DayData[];
}

// Interface para os itens de status no StatusDistributionChart
interface StatusItem {
  status: string;
  count: number;
  color?: string;
}

// Interface para as props do componente StatusDistributionChart
interface StatusDistributionChartProps {
  data: StatusItem[];
}

// Interface para os itens do funcionário na tabela
interface EmployeeItem {
  nome: string;
  matricula: string | number;
  diasTrabalhados: number;
  horasTrabalhadas: string | number;
  horasExtras: string | number;
  horasFaltantes: string | number;
  status: string;
}

// Interface para as props da tabela de funcionários
interface EmployeeTableProps {
  data: EmployeeItem[];
  title?: string;
  period?: string;
}

// Interface para os dados de departamento
interface DepartmentData {
  nome: string;
  totalServidores: number;
  mediaHorasTrabalhadas: string | number;
  totalHorasExtras: string | number;
  totalHorasFaltantes: string | number;
  percentualRegular: number;
}

// Interface para as props da tabela de departamentos
interface DepartmentTableProps {
  data: DepartmentData[];
  title?: string;
  sortable?: boolean;
}

// Interface para os dados do relatório
interface ReportData {
  dailyHours: DayData[];
  statusDistribution: StatusItem[];
  summaryData: EmployeeItem[];
  departmentData: DepartmentData[];
}

// ======= COMPONENTES =======

// Componente para seleção de período
const PeriodSelector = ({ period, setPeriod }: PeriodSelectorProps) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div>
        <label htmlFor="startDate" className="block text-sm font-medium text-gray-700 mb-1">
          Data Início
        </label>
        <input
          type="date"
          id="startDate"
          name="startDate"
          value={period.startDate}
          onChange={(e) => setPeriod({ ...period, startDate: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
      
      <div>
        <label htmlFor="endDate" className="block text-sm font-medium text-gray-700 mb-1">
          Data Fim
        </label>
        <input
          type="date"
          id="endDate"
          name="endDate"
          value={period.endDate}
          onChange={(e) => setPeriod({ ...period, endDate: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
      
      <div>
        <label htmlFor="reportType" className="block text-sm font-medium text-gray-700 mb-1">
          Tipo de Relatório
        </label>
        <select
          id="reportType"
          name="reportType"
          value={period.reportType}
          onChange={(e) => setPeriod({ ...period, reportType: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="individual">Individual</option>
          <option value="department">Por Departamento</option>
          <option value="summary">Resumo Geral</option>
        </select>
      </div>
    </div>
  );
};

// Componente para filtros adicionais
const AdditionalFilters = ({ filters, setFilters }: AdditionalFiltersProps) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
      <div>
        <label htmlFor="servidor" className="block text-sm font-medium text-gray-700 mb-1">
          Servidor
        </label>
        <input
          type="text"
          id="servidor"
          name="servidor"
          value={filters.servidor}
          onChange={(e) => setFilters({ ...filters, servidor: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          placeholder="Nome ou matrícula"
        />
      </div>
      
      <div>
        <label htmlFor="secretaria" className="block text-sm font-medium text-gray-700 mb-1">
          Secretaria
        </label>
        <select
          id="secretaria"
          name="secretaria"
          value={filters.secretaria}
          onChange={(e) => setFilters({ ...filters, secretaria: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Todas</option>
          <option value="administracao">Secretaria de Administração</option>
          <option value="educacao">Secretaria de Educação</option>
          <option value="saude">Secretaria de Saúde</option>
          <option value="obras">Secretaria de Obras</option>
        </select>
      </div>
      
      <div>
        <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
          Status
        </label>
        <select
          id="status"
          name="status"
          value={filters.status}
          onChange={(e) => setFilters({ ...filters, status: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Todos</option>
          <option value="regular">Regular</option>
          <option value="irregular">Irregular</option>
          <option value="justificado">Justificado</option>
        </select>
      </div>
    </div>
  );
};

// Componente para opções de exportação
const ExportOptions = ({ onExport }: ExportOptionsProps) => {
  return (
    <div className="flex space-x-2 mt-4">
      <button
        onClick={() => onExport('pdf')}
        className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
      >
        Exportar PDF
      </button>
      <button
        onClick={() => onExport('excel')}
        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
      >
        Exportar Excel
      </button>
      <button
        onClick={() => onExport('csv')}
        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      >
        Exportar CSV
      </button>
    </div>
  );
};

// Componente para gráfico de horas trabalhadas
const WorkHoursChart = ({ data }: WorkHoursChartProps) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mt-6">
      <h3 className="text-lg font-medium text-gray-800 mb-4">Horas Trabalhadas por Dia</h3>
      <div className="h-64 w-full">
        <div className="flex items-end h-48 space-x-2">
          {data.map((day, index) => (
            <div key={index} className="flex flex-col items-center flex-1">
              <div 
                className="w-full bg-blue-500 rounded-t"
                style={{ 
                  height: `${(day.hoursWorked / 10) * 100}%`,
                  maxHeight: '100%'
                }}
              ></div>
              <span className="text-xs mt-1">{day.date}</span>
            </div>
          ))}
        </div>
        <div className="flex justify-between mt-2">
          <span className="text-xs text-gray-500">0h</span>
          <span className="text-xs text-gray-500">10h</span>
        </div>
      </div>
    </div>
  );
};

// Componente para gráfico de distribuição de status
const StatusDistributionChart = ({ data }: StatusDistributionChartProps) => {
  const total = data.reduce((acc, item) => acc + item.count, 0);
  
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mt-6">
      <h3 className="text-lg font-medium text-gray-800 mb-4">Distribuição de Status</h3>
      <div className="flex h-8 w-full rounded-full overflow-hidden">
        {data.map((item, index) => (
          <div 
            key={index}
            className={`${
              item.status === 'Regular' ? 'bg-green-500' : 
              item.status === 'Irregular' ? 'bg-red-500' : 
              'bg-yellow-500'
            }`}
            style={{ width: `${(item.count / total) * 100}%` }}
          ></div>
        ))}
      </div>
      <div className="flex justify-between mt-4">
        {data.map((item, index) => (
          <div key={index} className="flex items-center">
            <div className={`w-3 h-3 rounded-full mr-1 ${
              item.status === 'Regular' ? 'bg-green-500' : 
              item.status === 'Irregular' ? 'bg-red-500' : 
              'bg-yellow-500'
            }`}></div>
            <span className="text-xs text-gray-700">{item.status}: {item.count} ({Math.round((item.count / total) * 100)}%)</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// Componente para tabela de resumo de funcionários
const SummaryTable = ({ data, title }: EmployeeTableProps) => {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden mt-6">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-800">{title || 'Resumo por Servidor'}</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Servidor</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Matrícula</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Dias Trabalhados</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Horas Trabalhadas</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Horas Extras</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Horas Faltantes</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((item, index) => (
              <tr key={index}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.nome}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.matricula}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.diasTrabalhados}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.horasTrabalhadas}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.horasExtras}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.horasFaltantes}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    item.status === 'Regular' ? 'bg-green-100 text-green-800' : 
                    item.status === 'Irregular' ? 'bg-red-100 text-red-800' : 
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {item.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Componente para tabela de departamentos
const DepartmentTable = ({ data, title, sortable = true }: DepartmentTableProps) => {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden mt-6">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-800">{title || 'Resumo por Departamento'}</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Departamento</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Servidores</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Média Horas Trabalhadas</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Horas Extras</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Horas Faltantes</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">% Regular</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((item, index) => (
              <tr key={index}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.nome}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.totalServidores}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.mediaHorasTrabalhadas}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.totalHorasExtras}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.totalHorasFaltantes}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.percentualRegular}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Página principal de relatórios
export default function RelatoriosPage() {
  const router = useRouter();
  const { api, isLoading, setLoading, error, setError } = useApi();
  
  const [period, setPeriod] = useState<Period>({
    startDate: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0],
    reportType: 'individual'
  });
  
  const [filters, setFilters] = useState<Filters>({
    servidor: '',
    secretaria: '',
    status: ''
  });
  
  const [reportData, setReportData] = useState<ReportData>({
    dailyHours: [],
    statusDistribution: [],
    summaryData: [],
    departmentData: []
  });
  
  const [showReport, setShowReport] = useState(false);
  
  // Função para gerar relatório
  const generateReport = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Em um cenário real, buscaríamos esses dados da API
      // Por enquanto, vamos simular com dados estáticos
      
      // Simular uma chamada de API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Dados simulados para o gráfico de horas trabalhadas
      const dailyHoursData: DayData[] = [];
      const startDate = new Date(period.startDate);
      const endDate = new Date(period.endDate);
      const dayDiff = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 3600 * 24));
      
      for (let i = 0; i <= Math.min(dayDiff, 14); i++) {
        const currentDate = new Date(startDate);
        currentDate.setDate(startDate.getDate() + i);
        
        // Pular finais de semana
        if (currentDate.getDay() === 0 || currentDate.getDay() === 6) {
          continue;
        }
        
        dailyHoursData.push({
          date: `${currentDate.getDate().toString().padStart(2, '0')}/${(currentDate.getMonth() + 1).toString().padStart(2, '0')}`,
          hoursWorked: Math.random() * 2 + 7 // Entre 7 e 9 horas
        });
      }
      
      // Dados simulados para a distribuição de status
      const statusDistributionData: StatusItem[] = [
        { status: 'Regular', count: Math.floor(Math.random() * 50) + 150 },
        { status: 'Irregular', count: Math.floor(Math.random() * 20) + 10 },
        { status: 'Justificado', count: Math.floor(Math.random() * 15) + 5 }
      ];
      
      // Dados simulados para a tabela de resumo
      const summaryData: EmployeeItem[] = [
        {
          nome: 'João Silva',
          matricula: '00003347',
          diasTrabalhados: 22,
          horasTrabalhadas: '176:00',
          horasExtras: '8:00',
          horasFaltantes: '0:00',
          status: 'Regular'
        },
        {
          nome: 'Maria Oliveira',
          matricula: '00004521',
          diasTrabalhados: 21,
          horasTrabalhadas: '168:00',
          horasExtras: '0:00',
          horasFaltantes: '8:00',
          status: 'Regular'
        },
        {
          nome: 'Carlos Santos',
          matricula: '00002189',
          diasTrabalhados: 18,
          horasTrabalhadas: '144:00',
          horasExtras: '0:00',
          horasFaltantes: '32:00',
          status: 'Irregular'
        },
        {
          nome: 'Ana Pereira',
          matricula: '00005632',
          diasTrabalhados: 20,
          horasTrabalhadas: '160:00',
          horasExtras: '0:00',
          horasFaltantes: '16:00',
          status: 'Justificado'
        },
        {
          nome: 'Pedro Souza',
          matricula: '00001478',
          diasTrabalhados: 22,
          horasTrabalhadas: '176:00',
          horasExtras: '4:00',
          horasFaltantes: '0:00',
          status: 'Regular'
        }
      ];
      
      // Dados simulados para a tabela de departamentos
      const departmentData: DepartmentData[] = [
        {
          nome: 'Secretaria de Administração',
          totalServidores: 45,
          mediaHorasTrabalhadas: '165:30',
          totalHorasExtras: '120:00',
          totalHorasFaltantes: '80:00',
          percentualRegular: 85
        },
        {
          nome: 'Secretaria de Educação',
          totalServidores: 120,
          mediaHorasTrabalhadas: '170:15',
          totalHorasExtras: '240:00',
          totalHorasFaltantes: '160:00',
          percentualRegular: 78
        },
        {
          nome: 'Secretaria de Saúde',
          totalServidores: 80,
          mediaHorasTrabalhadas: '168:45',
          totalHorasExtras: '320:00',
          totalHorasFaltantes: '40:00',
          percentualRegular: 92
        },
        {
          nome: 'Secretaria de Obras',
          totalServidores: 35,
          mediaHorasTrabalhadas: '172:20',
          totalHorasExtras: '180:00',
          totalHorasFaltantes: '60:00',
          percentualRegular: 80
        }
      ];
      
      setReportData({
        dailyHours: dailyHoursData,
        statusDistribution: statusDistributionData,
        summaryData: summaryData,
        departmentData: departmentData
      });
      
      setShowReport(true);
    } catch (err) {
      console.error('Erro ao gerar relatório:', err);
      setError('Não foi possível gerar o relatório. Por favor, tente novamente mais tarde.');
    } finally {
      setLoading(false);
    }
  };
  
  // Função para exportar relatório
  const handleExport = (format: string) => {
    alert(`Exportando relatório em formato ${format.toUpperCase()}. Esta funcionalidade seria implementada com bibliotecas específicas para cada formato.`);
  };
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Relatórios Avançados</h1>
          <p className="text-gray-600">Gere relatórios personalizados com visualizações detalhadas</p>
        </div>
        <button
          onClick={() => router.back()}
          className="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200"
        >
          Voltar
        </button>
      </div>
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-medium text-gray-700 mb-4">Configurações do Relatório</h3>
        
        <PeriodSelector period={period} setPeriod={setPeriod} />
        
        <AdditionalFilters filters={filters} setFilters={setFilters} />
        
        <div className="mt-6 flex justify-end">
          <button
            onClick={generateReport}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {isLoading ? 'Gerando...' : 'Gerar Relatório'}
          </button>
        </div>
      </div>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Erro! </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}
      
      {showReport && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-800">Resultado do Relatório</h3>
              <ExportOptions onExport={handleExport} />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <WorkHoursChart data={reportData.dailyHours} />
              <StatusDistributionChart data={reportData.statusDistribution} />
            </div>
          </div>
          
          {period.reportType === 'individual' && (
            <SummaryTable data={reportData.summaryData} />
          )}
          
          {period.reportType === 'department' && (
            <DepartmentTable data={reportData.departmentData} />
          )}
          
          {period.reportType === 'summary' && (
            <>
              <SummaryTable data={reportData.summaryData} />
              <DepartmentTable data={reportData.departmentData} />
            </>
          )}
        </div>
      )}
    </div>
  );
}