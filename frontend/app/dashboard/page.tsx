'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/auth-context';
import { dashboardService } from '../services/api';

// Componente de Card para estatísticas
const StatCard = ({ title, value, icon }: { title: string; value: string; icon: React.ReactNode }) => (
  <div className="bg-white rounded-lg shadow-md p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-500">{title}</p>
        <p className="text-2xl font-semibold mt-1">{value}</p>
      </div>
      <div className="text-blue-500">{icon}</div>
    </div>
  </div>
);

// Componente de Tabela para atividades recentes
const RecentActivitiesTable = ({ activities }: { activities: any[] }) => (
  <div className="bg-white rounded-lg shadow-md overflow-hidden">
    <div className="px-6 py-4 border-b border-gray-200">
      <h3 className="text-lg font-semibold text-gray-800">Atividades Recentes</h3>
    </div>
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Servidor</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tipo</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Data</th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {activities.map((activity, index) => (
            <tr key={index}>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-gray-900">{activity.servidor}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-500">{activity.tipo}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm text-gray-500">{activity.data}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                  activity.status === 'Aprovado' ? 'bg-green-100 text-green-800' : 
                  activity.status === 'Pendente' ? 'bg-yellow-100 text-yellow-800' : 
                  'bg-red-100 text-red-800'
                }`}>
                  {activity.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

// Página principal do Dashboard
export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    servidores: '0',
    batidasHoje: '0',
    justificativasPendentes: '0',
    diasIrregulares: '0'
  });
  const [activities, setActivities] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Buscar estatísticas do dashboard
        const statsData = await dashboardService.getStats();
        setStats({
          servidores: statsData.total_servidores.toString(),
          batidasHoje: statsData.batidas_hoje.toString(),
          justificativasPendentes: statsData.justificativas_pendentes.toString(),
          diasIrregulares: statsData.dias_irregulares.toString()
        });
        
        // Buscar atividades recentes
        const activitiesData = await dashboardService.getRecentActivities();
        setActivities(activitiesData);
      } catch (err: any) {
        console.error('Erro ao buscar dados do dashboard:', err);
        setError('Não foi possível carregar os dados do dashboard. Por favor, tente novamente mais tarde.');
        
        // Dados simulados para desenvolvimento
        setStats({
          servidores: '245',
          batidasHoje: '532',
          justificativasPendentes: '18',
          diasIrregulares: '37'
        });
        
        setActivities([
          { servidor: 'João Silva', tipo: 'Justificativa', data: '27/04/2025', status: 'Pendente' },
          { servidor: 'Maria Oliveira', tipo: 'Batida', data: '27/04/2025', status: 'Aprovado' },
          { servidor: 'Carlos Santos', tipo: 'Justificativa', data: '26/04/2025', status: 'Rejeitado' },
          { servidor: 'Ana Pereira', tipo: 'Batida', data: '26/04/2025', status: 'Aprovado' },
          { servidor: 'Pedro Souza', tipo: 'Justificativa', data: '25/04/2025', status: 'Pendente' }
        ]);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Erro! </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}
      
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
        <p className="text-gray-600">Bem-vindo, {user?.nome_completo || user?.name || user?.full_name || user?.username || (user?.email ? user.email.split('@')[0] : 'Usuário')}!</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="Total de Servidores" 
          value={stats.servidores} 
          icon={
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          } 
        />
        
        <StatCard 
          title="Batidas Hoje" 
          value={stats.batidasHoje} 
          icon={
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          } 
        />
        
        <StatCard 
          title="Justificativas Pendentes" 
          value={stats.justificativasPendentes} 
          icon={
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          } 
        />
        
        <StatCard 
          title="Dias Irregulares" 
          value={stats.diasIrregulares} 
          icon={
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          } 
        />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentActivitiesTable activities={activities} />
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Ações Rápidas</h3>
          
          <div className="space-y-4">
            <a href="/dashboard/batidas/importar" className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
              <div className="flex items-center">
                <div className="bg-blue-100 p-3 rounded-lg">
                  <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                  </svg>
                </div>
                <div className="ml-4">
                  <h4 className="text-base font-medium text-gray-900">Importar Batidas</h4>
                  <p className="text-sm text-gray-500">Importe arquivos de batidas para processamento</p>
                </div>
              </div>
            </a>
            
            <a href="/dashboard/justificativas" className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
              <div className="flex items-center">
                <div className="bg-green-100 p-3 rounded-lg">
                  <svg className="w-6 h-6 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <h4 className="text-base font-medium text-gray-900">Aprovar Justificativas</h4>
                  <p className="text-sm text-gray-500">Revise e aprove justificativas pendentes</p>
                </div>
              </div>
            </a>
            
            <a href="/dashboard/relatorios" className="block p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
              <div className="flex items-center">
                <div className="bg-purple-100 p-3 rounded-lg">
                  <svg className="w-6 h-6 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <h4 className="text-base font-medium text-gray-900">Gerar Relatórios</h4>
                  <p className="text-sm text-gray-500">Crie relatórios e espelhos de ponto</p>
                </div>
              </div>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
