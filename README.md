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

### Requisitos do Sistema
- Docker 20.10.0 ou superior
- Docker Compose 2.0.0 ou superior
- Git 2.0.0 ou superior
- Mínimo de 2GB de RAM disponível
- 10GB de espaço em disco

### Requisitos para Desenvolvimento
- Python 3.9+
- Node.js 18+ (para desenvolvimento frontend)
- npm 8+ ou yarn 1.22+

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
# Construir as imagens (primeira vez apenas)
docker-compose build

# Iniciar os serviços
docker-compose up -d

# Executar as migrações do banco de dados
docker-compose exec app alembic upgrade head

# Carregar dados iniciais (opcional)
docker-compose exec app python -m app.db.seeds
```

4. Acesse as interfaces:
- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:3000
- PGAdmin: http://localhost:5050 (login com admin@example.com / admin)

## Desenvolvimento

### Configuração do Ambiente de Desenvolvimento

1. Backend (Python):
```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Instalar dependências
pip install -r requirements.txt
```

2. Frontend (Next.js):
```bash
cd frontend
npm install   # ou yarn install
```

### Comandos Úteis

```bash
# Executar testes
docker-compose exec app pytest

# Verificar logs em tempo real
docker-compose logs -f

# Reiniciar um serviço específico
docker-compose restart app  # ou frontend, db, etc.

# Limpar todos os dados e reconstruir
docker-compose down -v
docker-compose up -d --build
```

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

1. **Erro de Conexão com o Banco de Dados**
   - Verifique se as variáveis de ambiente no `.env` estão corretas
   - Confirme se o container do PostgreSQL está rodando: `docker-compose ps`
   - Verifique os logs do banco: `docker-compose logs db`

2. **Frontend Não Acessível**
   - Verifique se o container está rodando: `docker-compose ps frontend`
   - Confira os logs: `docker-compose logs frontend`
   - Verifique se as portas não estão em uso por outros serviços

3. **Erro ao Processar Batidas**
   - Verifique o formato dos arquivos de batida (CSV)
   - Confirme as permissões de escrita nos diretórios de upload
   - Consulte os logs do serviço: `docker-compose logs app`

4. **Problemas com WhatsApp**
   - Verifique a conexão com a API do WhatsApp
   - Confirme as credenciais no arquivo `.env`
   - Verifique os logs de integração

### Monitoramento e Diagnóstico

```bash
# Monitorar uso de recursos
docker stats

# Verificar status dos containers
docker-compose ps

# Inspecionar configurações
docker-compose config

# Backup do banco de dados
docker-compose exec db pg_dump -U postgres pontualagent > backup.sql
```

## Segurança

### Boas Práticas

1. **Senhas e Credenciais**
   - Altere todas as senhas padrão após a instalação
   - Use senhas fortes (mínimo 12 caracteres)
   - Ative autenticação de dois fatores quando disponível

2. **Ambiente de Produção**
   - Configure HTTPS usando certificados SSL
   - Mantenha o sistema e dependências atualizados
   - Faça backup regular dos dados
   - Monitore os logs de acesso

3. **Permissões**
   - Revise periodicamente as permissões dos usuários
   - Aplique o princípio do menor privilégio
   - Mantenha registros de auditoria

## Roadmap

### Próximas Funcionalidades

- [ ] Implementação de autenticação biométrica
- [ ] Integração com sistemas de RH
- [ ] App mobile para registro de ponto
- [ ] Dashboard personalizado por departamento
- [ ] Exportação de relatórios em novos formatos
- [ ] Módulo de banco de horas avançado

### Em Desenvolvimento

- [ ] Melhorias na interface do usuário
- [ ] Otimização do processamento de batidas
- [ ] Novos tipos de relatórios
- [ ] Integração com calendário corporativo

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
