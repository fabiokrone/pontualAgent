'use client';

import { useState, useEffect, Suspense } from 'react'; // Adicione o import do Suspense
import { useRouter, useSearchParams } from 'next/navigation';


// Componente que usa useSearchParams
function VisualizarPonto() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const matricula = searchParams.get('matricula');
  const [isLoading, setIsLoading] = useState(true);
  const [servidor, setServidor] = useState<any>(null);
  const [periodo, setPeriodo] = useState({
    mesAno: new Date().toISOString().substring(0, 7), // Formato YYYY-MM
  });
  const [espelhoPonto, setEspelhoPonto] = useState<any[]>([]);
  const [resumo, setResumo] = useState({
    totalDias: 0,
    diasTrabalhados: 0,
    horasTrabalhadas: '00:00',
    horasExtras: '00:00',
    horasFaltantes: '00:00',
    diasJustificados: 0,
  });

  // Buscar dados do servidor e espelho de ponto
  useEffect(() => {
    if (!matricula) return;

    const fetchData = async () => {
      setIsLoading(true);
      try {
        // Em um cenário real, buscaríamos esses dados da API
        // Por enquanto, vamos simular com dados estáticos
        
        // Simular uma chamada de API
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Dados simulados do servidor
        setServidor({
          id: 1,
          nome: 'João Silva',
          matricula: matricula,
          cpf: '123.456.789-00',
          email: 'joao.silva@exemplo.com',
          telefone: '(11) 98765-4321',
          secretaria: 'Secretaria de Administração',
          cargo: 'Analista Administrativo',
          dataAdmissao: '01/03/2020',
        });
        
        // Dados simulados do espelho de ponto
        const diasNoMes = new Date(parseInt(periodo.mesAno.split('-')[0]), parseInt(periodo.mesAno.split('-')[1]), 0).getDate();
        const espelho = [];
        
        let diasTrabalhados = 0;
        let horasTrabalhadasTotal = 0;
        let horasExtrasTotal = 0;
        let horasFaltantesTotal = 0;
        let diasJustificados = 0;
        
        for (let dia = 1; dia <= diasNoMes; dia++) {
          const data = new Date(parseInt(periodo.mesAno.split('-')[0]), parseInt(periodo.mesAno.split('-')[1]) - 1, dia);
          const diaSemana = data.getDay(); // 0 = Domingo, 6 = Sábado
          
          // Pular finais de semana
          if (diaSemana === 0 || diaSemana === 6) {
            espelho.push({
              data: `${dia.toString().padStart(2, '0')}/${periodo.mesAno.split('-')[1]}/${periodo.mesAno.split('-')[0]}`,
              diaSemana: ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'][diaSemana],
              batidas: [],
              horasTrabalhadas: '00:00',
              horasExtras: '00:00',
              horasFaltantes: '00:00',
              status: 'Final de Semana',
              observacao: '',
            });
            continue;
          }
          
          // Simular dias aleatórios com batidas
          const temBatidas = Math.random() > 0.2; // 80% de chance de ter batidas
          
          if (temBatidas) {
            diasTrabalhados++;
            
            // Simular batidas regulares (entrada 8h, saída 12h, entrada 13h, saída 17h)
            const batidas = [
              { hora: '08:00', tipo: 'Entrada' },
              { hora: '12:00', tipo: 'Saída' },
              { hora: '13:00', tipo: 'Entrada' },
              { hora: '17:00', tipo: 'Saída' },
            ];
            
            // Adicionar variação aleatória às batidas
            batidas.forEach(batida => {
              const [hora, minuto] = batida.hora.split(':').map(Number);
              const variacaoMinutos = Math.floor(Math.random() * 10) - 5; // -5 a +5 minutos
              const novoMinuto = Math.max(0, Math.min(59, minuto + variacaoMinutos));
              batida.hora = `${hora.toString().padStart(2, '0')}:${novoMinuto.toString().padStart(2, '0')}`;
            });
            
            // Calcular horas trabalhadas
            const horasTrabalhadas = 8; // 8 horas padrão
            horasTrabalhadasTotal += horasTrabalhadas;
            
            // Simular horas extras ou faltantes
            const variacao = Math.random() > 0.7 ? (Math.random() > 0.5 ? 1 : -1) : 0; // 30% de chance de ter variação
            
            let horasExtras = 0;
            let horasFaltantes = 0;
            
            if (variacao > 0) {
              horasExtras = variacao;
              horasExtrasTotal += horasExtras;
            } else if (variacao < 0) {
              horasFaltantes = Math.abs(variacao);
              horasFaltantesTotal += horasFaltantes;
            }
            
            // Determinar status
            let status = 'Regular';
            let observacao = '';
            
            if (horasFaltantes > 0) {
              // 30% de chance de ser justificada
              if (Math.random() > 0.7) {
                status = 'Justificada';
                observacao = 'Justificativa aprovada pelo gestor';
                diasJustificados++;
              } else {
                status = 'Irregular';
                observacao = 'Horas faltantes não justificadas';
              }
            } else if (horasExtras > 0) {
              status = 'Regular';
              observacao = 'Horas extras registradas';
            }
            
            espelho.push({
              data: `${dia.toString().padStart(2, '0')}/${periodo.mesAno.split('-')[1]}/${periodo.mesAno.split('-')[0]}`,
              diaSemana: ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'][diaSemana],
              batidas,
              horasTrabalhadas: `${Math.floor(horasTrabalhadas)}:${((horasTrabalhadas % 1) * 60).toString().padStart(2, '0')}`,
              horasExtras: horasExtras > 0 ? `${Math.floor(horasExtras)}:${((horasExtras % 1) * 60).toString().padStart(2, '0')}` : '00:00',
              horasFaltantes: horasFaltantes > 0 ? `${Math.floor(horasFaltantes)}:${((horasFaltantes % 1) * 60).toString().padStart(2, '0')}` : '00:00',
              status,
              observacao,
            });
          } else {
            // Dia sem batidas
            espelho.push({
              data: `${dia.toString().padStart(2, '0')}/${periodo.mesAno.split('-')[1]}/${periodo.mesAno.split('-')[0]}`,
              diaSemana: ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'][diaSemana],
              batidas: [],
              horasTrabalhadas: '00:00',
              horasExtras: '00:00',
              horasFaltantes: '08:00',
              status: Math.random() > 0.5 ? 'Justificada' : 'Irregular',
              observacao: Math.random() > 0.5 ? 'Falta justificada (atestado médico)' : 'Falta não justificada',
            });
            
            if (espelho[espelho.length - 1].status === 'Justificada') {
              diasJustificados++;
            }
            
            horasFaltantesTotal += 8;
          }
        }
        
        setEspelhoPonto(espelho);
        
        // Atualizar resumo
        setResumo({
          totalDias: diasNoMes,
          diasTrabalhados,
          horasTrabalhadas: `${Math.floor(horasTrabalhadasTotal)}:${((horasTrabalhadasTotal % 1) * 60).toString().padStart(2, '0')}`,
          horasExtras: `${Math.floor(horasExtrasTotal)}:${((horasExtrasTotal % 1) * 60).toString().padStart(2, '0')}`,
          horasFaltantes: `${Math.floor(horasFaltantesTotal)}:${((horasFaltantesTotal % 1) * 60).toString().padStart(2, '0')}`,
          diasJustificados,
        });
      } catch (error) {
        console.error('Erro ao buscar dados:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [matricula, periodo.mesAno]);

  const handlePeriodoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPeriodo({ ...periodo, mesAno: e.target.value });
  };

  const handleImprimir = () => {
    window.print();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 print:space-y-4">
      <div className="flex items-center justify-between print:hidden">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Espelho de Ponto</h1>
          <p className="text-gray-600">Visualize e imprima o espelho de ponto do servidor</p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => router.back()}
            className="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded-md hover:bg-gray-200"
          >
            Voltar
          </button>
          <button
            onClick={handleImprimir}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Imprimir
          </button>
        </div>
      </div>
      
      <div className="bg-white rounded-lg shadow-md p-6 print:shadow-none print:p-0">
        <div className="print:flex print:justify-between print:items-center">
          <div className="print:text-center">
            <h2 className="text-xl font-bold text-center print:text-2xl">ESPELHO DE PONTO</h2>
            <p className="text-gray-600 text-center print:text-lg">Período: {periodo.mesAno.split('-')[1]}/{periodo.mesAno.split('-')[0]}</p>
          </div>
          <div className="print:hidden mb-6 flex justify-end">
            <div className="w-64">
              <label htmlFor="periodo" className="block text-sm font-medium text-gray-700 mb-1">
                Selecione o Período
              </label>
              <input
                type="month"
                id="periodo"
                name="periodo"
                value={periodo.mesAno}
                onChange={handlePeriodoChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>
        
        <div className="mt-6 print:mt-4">
          <h3 className="text-lg font-medium text-gray-800 mb-2">Dados do Servidor</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 print:grid-cols-2">
            <div>
              <p className="text-sm text-gray-600">Nome:</p>
              <p className="font-medium">{servidor?.nome}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Matrícula:</p>
              <p className="font-medium">{servidor?.matricula}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Cargo:</p>
              <p className="font-medium">{servidor?.cargo}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Secretaria:</p>
              <p className="font-medium">{servidor?.secretaria}</p>
            </div>
          </div>
        </div>
        
        <div className="mt-6 print:mt-4">
          <h3 className="text-lg font-medium text-gray-800 mb-2">Resumo do Período</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 print:grid-cols-3">
            <div className="bg-gray-50 p-3 rounded print:bg-white print:border print:border-gray-300">
              <p className="text-sm text-gray-600">Dias Trabalhados:</p>
              <p className="text-xl font-medium">{resumo.diasTrabalhados} / {resumo.totalDias - 8}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded print:bg-white print:border print:border-gray-300">
              <p className="text-sm text-gray-600">Horas Trabalhadas:</p>
              <p className="text-xl font-medium">{resumo.horasTrabalhadas}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded print:bg-white print:border print:border-gray-300">
              <p className="text-sm text-gray-600">Horas Extras:</p>
              <p className="text-xl font-medium">{resumo.horasExtras}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded print:bg-white print:border print:border-gray-300">
              <p className="text-sm text-gray-600">Horas Faltantes:</p>
              <p className="text-xl font-medium">{resumo.horasFaltantes}</p>
            </div>
            <div className="bg-gray-50 p-3 rounded print:bg-white print:border print:border-gray-300">
              <p className="text-sm text-gray-600">Dias Justificados:</p>
              <p className="text-xl font-medium">{resumo.diasJustificados}</p>
            </div>
          </div>
        </div>
        
        <div className="mt-6 print:mt-4">
          <h3 className="text-lg font-medium text-gray-800 mb-2">Detalhamento Diário</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 print:border print:border-gray-300">
              <thead className="bg-gray-50 print:bg-gray-100">
                <tr>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Data</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Dia</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Batidas</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Horas Trab.</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Extras</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Faltantes</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Observação</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {espelhoPonto.map((dia, index) => (
                  <tr key={index} className={dia.status === 'Final de Semana' ? 'bg-gray-50' : ''}>
                    <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-500">{dia.data}</td>
                    <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-500">{dia.diaSemana}</td>
                    <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-500">
                      {dia.batidas.map((batida: { hora: string; tipo: string }, i: number) => (                      
                        <span key={i}>
                          {batida.hora} ({batida.tipo}){i < dia.batidas.length - 1 ? ', ' : ''}
                        </span>
                      ))}
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-500">{dia.horasTrabalhadas}</td>
                    <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-500">{dia.horasExtras}</td>
                    <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-500">{dia.horasFaltantes}</td>
                    <td className="px-3 py-2 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        dia.status === 'Regular' ? 'bg-green-100 text-green-800' : 
                        dia.status === 'Irregular' ? 'bg-red-100 text-red-800' : 
                        dia.status === 'Justificada' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {dia.status}
                      </span>
                    </td>
                    <td className="px-3 py-2 whitespace-nowrap text-sm text-gray-500">{dia.observacao}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
        
        <div className="mt-8 print:mt-12 print:pt-8 print:border-t print:border-gray-300">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 print:grid-cols-2">
            <div className="text-center">
              <div className="border-t border-gray-300 pt-4 mt-16 mx-auto w-64"></div>
              <p className="text-sm text-gray-600">Assinatura do Servidor</p>
            </div>
            <div className="text-center">
              <div className="border-t border-gray-300 pt-4 mt-16 mx-auto w-64"></div>
              <p className="text-sm text-gray-600">Assinatura do Gestor</p>
            </div>
          </div>
        </div>
        
        <div className="mt-8 text-center text-sm text-gray-500 print:mt-12">
          <p>Documento gerado em {new Date().toLocaleDateString()} às {new Date().toLocaleTimeString()}</p>
          <p>PontoAgent - Sistema de Gestão de Ponto</p>
        </div>
      </div>
      
      <style jsx global>{`
        @media print {
          body {
            font-size: 12px;
          }
          
          @page {
            size: A4;
            margin: 1cm;
          }
          
          nav, footer, .print-hidden {
            display: none !important;
          }
        }
      `}</style>
    </div>
  );
}

// Componente principal que envolve com Suspense
export default function VisualizarPontoPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>}>
      <VisualizarPonto />
    </Suspense>
  );
}