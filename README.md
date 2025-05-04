# PontoAgent

Sistema de gestão de ponto automatizado com processamento inteligente de batidas e integração com WhatsApp.

## Visão Geral

O PontoAgent é uma solução completa para gestão de ponto eletrônico, desenvolvida com tecnologias modernas para automatizar o processamento de batidas de ponto, gerenciar justificativas e gerar relatórios detalhados. O sistema é composto por um backend robusto em FastAPI e um frontend intuitivo em Next.js.

## Funcionalidades Principais

- **Processamento Inteligente de Batidas**: Cálculo automático de horas trabalhadas, extras e faltas
- **Gestão de Justificativas**: Fluxo completo de solicitação e aprovação de justificativas
- **Relatórios Avançados**: Exportação em múltiplos formatos (PDF, Excel, CSV)
- **Integração com WhatsApp**: Notificações e alertas via mensagens
- **Painel Administrativo**: Interface intuitiva para gestores e administradores
- **Autenticação Segura**: Sistema de login com diferentes níveis de acesso

## Tecnologias Utilizadas

### Backend
- FastAPI (Python)
- PostgreSQL
- SQLAlchemy ORM
- Pydantic para validação de dados
- JWT para autenticação

### Frontend
- Next.js (React)
- TypeScript
- Tailwind CSS
- Context API para gerenciamento de estado

## Requisitos

- Docker e Docker Compose
- Git

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/fabiokrone/pontualAgent.git
cd pontualAgent
```

2. Configure o arquivo de variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env conforme necessário
```

3. Inicie os containers com Docker Compose:
```bash
docker-compose up -d
```

4. Acesse as interfaces:
- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:3000
- PGAdmin: http://localhost:5050 (login com admin@example.com / admin)

## Estrutura do Projeto

```
pontualAgent/
├── app/                  # Código backend
│   ├── api/              # Endpoints da API
│   ├── core/             # Configurações principais
│   ├── db/               # Configuração do banco de dados
│   ├── models/           # Modelos de dados
│   ├── schemas/          # Schemas Pydantic
│   └── services/         # Serviços de negócio
├── docker/               # Configurações Docker
│   ├── app/              # Dockerfile do backend
│   └── postgres/         # Scripts de inicialização do PostgreSQL
├── frontend/             # Interface web administrativa
│   ├── app/              # Código Next.js
│   ├── docs/             # Documentação do frontend
│   └── ...               # Outros arquivos do frontend
├── docs/                 # Documentação geral
├── docker-compose.yml    # Configuração Docker Compose
└── .env.example          # Exemplo de variáveis de ambiente
```

## Módulo de Relatórios Avançados

O sistema inclui um módulo completo de relatórios avançados que permite:

- Gerar relatórios personalizados por departamento, período ou servidor
- Visualizar dados em diferentes formatos gráficos
- Exportar relatórios em PDF, Excel e CSV
- Agendar envio automático de relatórios

Para acessar o módulo de relatórios, navegue até a seção "Relatórios" no menu lateral da interface administrativa.

## Autenticação e Autorização

O sistema implementa diferentes níveis de acesso:

- **Administrador**: Acesso completo a todas as funcionalidades
- **Gestor**: Aprovação de justificativas e visualização de relatórios
- **Usuário**: Registro de justificativas e visualização do próprio espelho de ponto

As credenciais padrão para o primeiro acesso são:
- Usuário: admin
- Senha: admin123

Recomendamos alterar a senha padrão no primeiro acesso.

## Integração com WhatsApp

O sistema pode ser integrado com o WhatsApp para envio de notificações sobre:

- Aprovação ou rejeição de justificativas
- Alertas de batidas irregulares
- Lembretes de ponto
- Envio de espelho de ponto mensal

Para configurar a integração, preencha as variáveis relacionadas ao WhatsApp no arquivo `.env`.

## Solução de Problemas

### Problemas Comuns

- **Erro de Conexão com o Banco de Dados**: Verifique se as variáveis de ambiente estão configuradas corretamente no arquivo `.env`.
- **Frontend Não Acessível**: Verifique os logs do container frontend com `docker-compose logs frontend`.
- **Erro ao Processar Batidas**: Verifique o formato dos arquivos de batida conforme a documentação.

### Logs e Diagnóstico

Para verificar os logs dos serviços:

```bash
# Ver logs de todos os serviços
docker-compose logs

# Ver logs de um serviço específico
docker-compose logs frontend
docker-compose logs app
```

## Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## Contato

Para suporte ou dúvidas, entre em contato através do email: fabiokrone10@gmail.com

---
Desenvolvido com ❤️ por Fábio krone
