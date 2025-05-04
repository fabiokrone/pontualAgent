# PontoAgent - Documentação da Implementação

## Visão Geral

O PontoAgent é um sistema automatizado de gestão de ponto que permite o processamento de batidas de ponto, gerenciamento de justificativas e comunicação via WhatsApp. O sistema foi desenvolvido utilizando FastAPI, PostgreSQL e SQLAlchemy, com uma arquitetura modular e escalável.

## Estrutura do Projeto

```
PontoAgent/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── auth.py
│   │   │   ├── batidas.py
│   │   │   ├── justificativas.py
│   │   │   ├── servidores.py
│   │   │   ├── usuarios.py
│   │   │   └── whatsapp.py
│   │   └── api.py
│   ├── core/
│   │   ├── auth.py
│   │   └── config.py
│   ├── db/
│   │   └── session.py
│   ├── models/
│   │   ├── batida.py
│   │   ├── justificativa.py
│   │   ├── servidor.py
│   │   └── usuario.py
│   ├── schemas/
│   │   ├── batida.py
│   │   ├── justificativa.py
│   │   ├── servidor.py
│   │   └── usuario.py
│   ├── services/
│   │   ├── ponto_processor.py
│   │   └── whatsapp_service.py
│   └── main.py
├── tests/
│   ├── test_auth.py
│   ├── test_ponto_processor.py
│   └── test_whatsapp_service.py
├── .env
├── .env.example
├── docker-compose.yml
└── requirements.txt
```

## Componentes Principais

### 1. Modelos de Dados (SQLAlchemy)

Os modelos de dados representam as entidades principais do sistema:

- **Servidor**: Representa um servidor público com informações como nome, matrícula, CPF, email, etc.
- **Batida**: Representa um registro de ponto, dividido em batidas originais (importadas) e batidas processadas.
- **Justificativa**: Representa uma justificativa para ausência ou irregularidade no ponto.
- **Usuário**: Representa um usuário do sistema com diferentes níveis de acesso (admin, gestor, usuário).

### 2. Schemas (Pydantic)

Os schemas definem a validação de dados e a serialização/deserialização para a API:

- Implementação de validadores personalizados para CPF, matrícula, etc.
- Schemas para criação, atualização e leitura de entidades.
- Schemas para filtros de busca e paginação.
- Schemas para operações específicas como aprovação de justificativas.

### 3. Endpoints da API

A API expõe os seguintes endpoints principais:

- **/api/servidores**: CRUD para servidores.
- **/api/batidas**: Gerenciamento de batidas de ponto.
- **/api/justificativas**: Gerenciamento de justificativas, incluindo fluxo de aprovação.
- **/api/auth**: Autenticação e gerenciamento de usuários.
- **/api/whatsapp**: Integração com WhatsApp para notificações.

### 4. Processador de Ponto

O componente `PontoProcessor` implementa a lógica de negócio para processamento de batidas de ponto:

- Cálculo de horas trabalhadas, extras e faltantes.
- Tratamento de feriados e fins de semana.
- Integração com justificativas.
- Geração de relatórios detalhados.

### 5. Sistema de Autenticação e Autorização

O sistema de autenticação utiliza JWT (JSON Web Tokens) para controle de acesso:

- Diferentes níveis de acesso: admin, gestor, usuário.
- Controle de acesso baseado em secretaria.
- Fluxo de aprovação de justificativas por gestores.
- Proteção de endpoints sensíveis.

### 6. Integração com WhatsApp

O sistema oferece integração com WhatsApp para notificações:

- Suporte para Evolution API e API oficial do WhatsApp.
- Envio de mensagens de texto e templates.
- Notificações sobre status de justificativas.
- Alertas sobre batidas irregulares.

## Fluxos Principais

### 1. Processamento de Batidas

1. Batidas são importadas do sistema de origem (formato específico).
2. O processador analisa as batidas por servidor e período.
3. Cada dia é processado individualmente, calculando horas trabalhadas, extras e faltantes.
4. Dias com irregularidades são marcados para justificativa.
5. Relatórios são gerados com detalhes do processamento.

### 2. Fluxo de Justificativas

1. Servidor ou gestor registra uma justificativa para um dia específico.
2. A justificativa fica com status "pendente".
3. Gestor da secretaria analisa a justificativa.
4. Gestor aprova ou rejeita a justificativa.
5. Servidor é notificado via WhatsApp sobre o status da justificativa.
6. Se aprovada, a justificativa é considerada no processamento do ponto.

### 3. Autenticação e Autorização

1. Usuário faz login com username e senha.
2. Sistema gera um token JWT com informações de perfil e secretaria.
3. Token é utilizado para autenticar requisições subsequentes.
4. Sistema verifica permissões baseadas no perfil e secretaria do usuário.
5. Apenas gestores podem aprovar justificativas de servidores da sua secretaria.

## Configuração

O sistema utiliza variáveis de ambiente para configuração, definidas no arquivo `.env`:

### Configurações da Aplicação
```
PROJECT_NAME=Sistema Automatizado de Gestão de Ponto
API_PREFIX=/api
CORS_ORIGINS=http://localhost,http://localhost:8000
DEBUG=True
```

### Configurações do Banco de Dados
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=gestao_ponto
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800
DB_ECHO_LOG=True
```

### Configurações de Autenticação
```
SECRET_KEY=chave_secreta_temporaria_para_desenvolvimento
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Configurações de WhatsApp
```
WHATSAPP_API_TYPE=official
WHATSAPP_API_URL=https://graph.facebook.com/v17.0
WHATSAPP_API_TOKEN=seu_token_aqui
WHATSAPP_PHONE_NUMBER_ID=seu_phone_number_id_aqui
```

## Testes

O sistema inclui testes unitários para os componentes principais:

- **test_ponto_processor.py**: Testes para a lógica de processamento de batidas.
- **test_auth.py**: Testes para o sistema de autenticação e autorização.
- **test_whatsapp_service.py**: Testes para a integração com WhatsApp.

## Próximos Passos

1. **Implementação de Relatórios**: Adicionar geração de relatórios em PDF para espelho de ponto.
2. **Dashboard**: Desenvolver um dashboard para visualização de métricas.
3. **Integração com Sistemas Externos**: Implementar integração com outros sistemas de RH.
4. **Melhorias na Interface**: Desenvolver uma interface web mais amigável.
5. **Escalabilidade**: Otimizar o processamento para grandes volumes de dados.

## Considerações de Segurança

1. **Proteção de Dados Sensíveis**: CPF e outros dados pessoais são validados e armazenados de forma segura.
2. **Autenticação Robusta**: Senhas são armazenadas com hash seguro (bcrypt).
3. **Controle de Acesso**: Implementação de RBAC (Role-Based Access Control).
4. **Validação de Entrada**: Todos os dados de entrada são validados com Pydantic.
5. **Proteção contra Ataques Comuns**: Implementação de medidas contra CSRF, XSS, etc.

## Conclusão

O PontoAgent oferece uma solução completa para gestão de ponto, com processamento automatizado, fluxo de aprovação de justificativas e integração com WhatsApp. A arquitetura modular permite fácil manutenção e extensão do sistema para atender a requisitos futuros.
