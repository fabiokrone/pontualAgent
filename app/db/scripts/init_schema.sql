-- =============================================
-- Sistema Automatizado de Gestão de Ponto
-- Esquema Completo com Tabelas e Triggers
-- =============================================

-- Criação do Schema
CREATE SCHEMA IF NOT EXISTS ponto;
SET search_path TO ponto, public;

-- Criação de domínios personalizados para maior consistência
CREATE DOMAIN email_type AS VARCHAR(100)
    CHECK (VALUE ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$');

CREATE DOMAIN telefone_type AS VARCHAR(20)
    CHECK (VALUE ~ '^\+?[0-9]{10,15}$');

CREATE DOMAIN status_justificativa_type AS VARCHAR(20)
    CHECK (VALUE IN ('pendente', 'aprovada', 'rejeitada'));

CREATE DOMAIN status_conversa_type AS VARCHAR(20)
    CHECK (VALUE IN ('ativa', 'finalizada', 'aguardando', 'cancelada'));

CREATE DOMAIN tipo_midia_type AS VARCHAR(20)
    CHECK (VALUE IN ('texto', 'imagem', 'audio', 'documento', 'video', 'contato', 'localizacao'));

-- Tabela de Secretarias/Departamentos
CREATE TABLE secretarias (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Servidores
CREATE TABLE servidores (
    id SERIAL PRIMARY KEY,
    matricula VARCHAR(20) UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    email email_type,
    telefone telefone_type,
    whatsapp telefone_type,
    secretaria_id INTEGER REFERENCES secretarias(id),
    cargo VARCHAR(100),
    ativo BOOLEAN DEFAULT TRUE,
    data_admissao DATE NOT NULL,
    data_demissao DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (data_demissao IS NULL OR data_demissao >= data_admissao)
);

-- Tabela para Horários Padrão dos Servidores
CREATE TABLE horarios_padrao (
    id SERIAL PRIMARY KEY,
    servidor_id INTEGER REFERENCES servidores(id) ON DELETE CASCADE,
    dia_semana INTEGER NOT NULL CHECK (dia_semana BETWEEN 0 AND 6), -- 0-6 (domingo-sábado)
    entrada_1 TIME,
    saida_1 TIME,
    entrada_2 TIME,
    saida_2 TIME,
    carga_horaria_diaria INTERVAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (servidor_id, dia_semana),
    CHECK (entrada_1 < saida_1),
    CHECK (entrada_2 IS NULL OR saida_2 IS NULL OR entrada_2 < saida_2),
    CHECK (saida_1 < entrada_2 OR entrada_2 IS NULL)
);

-- Tabela para Alterações Temporárias de Horário
CREATE TABLE alteracoes_horario (
    id SERIAL PRIMARY KEY,
    descricao TEXT NOT NULL,
    data_criacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    criado_por VARCHAR(100) NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    entrada_1 TIME,
    saida_1 TIME,
    entrada_2 TIME,
    saida_2 TIME,
    carga_horaria_diaria INTERVAL,
    comando_natural TEXT, -- Armazena o comando em linguagem natural que gerou a alteração
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (data_inicio <= data_fim),
    CHECK (entrada_1 IS NULL OR saida_1 IS NULL OR entrada_1 < saida_1),
    CHECK (entrada_2 IS NULL OR saida_2 IS NULL OR entrada_2 < saida_2),
    CHECK (saida_1 IS NULL OR entrada_2 IS NULL OR saida_1 < entrada_2)
);

-- Tabela para associar servidores às alterações de horário
CREATE TABLE alteracoes_horario_servidores (
    id SERIAL PRIMARY KEY,
    alteracao_id INTEGER REFERENCES alteracoes_horario(id) ON DELETE CASCADE,
    servidor_id INTEGER REFERENCES servidores(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (alteracao_id, servidor_id)
);

-- Tabela para associar secretarias às alterações de horário
CREATE TABLE alteracoes_horario_secretarias (
    id SERIAL PRIMARY KEY,
    alteracao_id INTEGER REFERENCES alteracoes_horario(id) ON DELETE CASCADE,
    secretaria_id INTEGER REFERENCES secretarias(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (alteracao_id, secretaria_id)
);

-- Tabela de Feriados e Pontos Facultativos
CREATE TABLE feriados (
    id SERIAL PRIMARY KEY,
    data DATE UNIQUE NOT NULL,
    descricao VARCHAR(100) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('feriado', 'ponto_facultativo')),
    ambito VARCHAR(20) NOT NULL CHECK (ambito IN ('nacional', 'estadual', 'municipal')),
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Batidas de Ponto (Originais)
CREATE TABLE batidas_originais (
    id SERIAL PRIMARY KEY,
    servidor_id INTEGER REFERENCES servidores(id) ON DELETE CASCADE,
    data_hora TIMESTAMP NOT NULL,
    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('entrada', 'saida')),
    dispositivo VARCHAR(50),
    localizacao VARCHAR(100),
    importado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    arquivo_origem VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Batidas de Ponto (Processadas/Autorizadas)
CREATE TABLE batidas_processadas (
    id SERIAL PRIMARY KEY,
    batida_original_id INTEGER REFERENCES batidas_originais(id) ON DELETE SET NULL,
    servidor_id INTEGER REFERENCES servidores(id) ON DELETE CASCADE,
    data_hora TIMESTAMP NOT NULL,
    tipo VARCHAR(10) NOT NULL CHECK (tipo IN ('entrada', 'saida')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('normal', 'justificada', 'ajustada', 'inconsistente')),
    processado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    justificativa_id INTEGER,
    processado_por VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Justificativas
CREATE TABLE justificativas (
    id SERIAL PRIMARY KEY,
    servidor_id INTEGER REFERENCES servidores(id) ON DELETE CASCADE,
    data DATE NOT NULL,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('atraso', 'saida_antecipada', 'falta', 'hora_extra', 'outros')),
    descricao TEXT NOT NULL,
    anexo_url VARCHAR(255),
    status status_justificativa_type NOT NULL DEFAULT 'pendente',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aprovado_por VARCHAR(100),
    aprovado_em TIMESTAMP,
    canal_origem VARCHAR(20) NOT NULL CHECK (canal_origem IN ('whatsapp', 'email', 'sistema')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Relatórios Gerados
CREATE TABLE relatorios (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('mensal', 'inconsistencias', 'horas_extras', 'justificativas', 'completo')),
    periodo_inicio DATE NOT NULL,
    periodo_fim DATE NOT NULL,
    secretaria_id INTEGER REFERENCES secretarias(id) ON DELETE SET NULL,
    servidor_id INTEGER REFERENCES servidores(id) ON DELETE SET NULL, -- Pode ser NULL se for relatório geral
    arquivo_url VARCHAR(255) NOT NULL,
    gerado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gerado_por VARCHAR(100),
    enviado BOOLEAN DEFAULT FALSE,
    enviado_em TIMESTAMP,
    destinatarios JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (periodo_inicio <= periodo_fim)
);

-- Tabela para log de comandos em linguagem natural
CREATE TABLE log_comandos_naturais (
    id SERIAL PRIMARY KEY,
    comando TEXT NOT NULL,
    interpretacao TEXT,
    executado BOOLEAN DEFAULT FALSE,
    erro TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executado_em TIMESTAMP,
    usuario VARCHAR(100),
    conversa_id INTEGER, -- Referência à conversa que gerou o comando
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Contatos WhatsApp
CREATE TABLE contatos_whatsapp (
    id SERIAL PRIMARY KEY,
    numero telefone_type UNIQUE NOT NULL,
    nome VARCHAR(100),
    servidor_id INTEGER REFERENCES servidores(id) ON DELETE SET NULL,
    is_gestor BOOLEAN DEFAULT FALSE,
    secretaria_id INTEGER REFERENCES secretarias(id) ON DELETE SET NULL,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_interacao TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Conversas WhatsApp
CREATE TABLE conversas_whatsapp (
    id SERIAL PRIMARY KEY,
    contato_id INTEGER REFERENCES contatos_whatsapp(id) ON DELETE CASCADE,
    status status_conversa_type NOT NULL DEFAULT 'ativa',
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('justificativa', 'alteracao_horario', 'relatorio', 'ajuste_ponto', 'consulta', 'outro')),
    iniciada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finalizada_em TIMESTAMP,
    ultima_interacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    contexto JSONB, -- Armazena o contexto da conversa (estado, dados coletados, etc.)
    resultado_acao TEXT, -- Descreve o resultado final da conversa (ex: "Justificativa registrada")
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Mensagens WhatsApp
CREATE TABLE mensagens_whatsapp (
    id SERIAL PRIMARY KEY,
    conversa_id INTEGER REFERENCES conversas_whatsapp(id) ON DELETE CASCADE,
    direcao VARCHAR(10) NOT NULL CHECK (direcao IN ('entrada', 'saida')),
    conteudo TEXT NOT NULL,
    tipo_midia tipo_midia_type DEFAULT 'texto',
    url_midia VARCHAR(255), -- URL para mídia (se aplicável)
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    lido BOOLEAN DEFAULT FALSE,
    lido_em TIMESTAMP,
    processado BOOLEAN DEFAULT FALSE,
    processado_em TIMESTAMP,
    resposta_para_id INTEGER REFERENCES mensagens_whatsapp(id) ON DELETE SET NULL, -- Para mensagens que são respostas diretas
    metadados_transcricao JSONB, -- Para armazenar metadados de transcrição de áudio
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela para Intenções de Conversa
CREATE TABLE intencoes_conversa (
    id SERIAL PRIMARY KEY,
    mensagem_id INTEGER REFERENCES mensagens_whatsapp(id) ON DELETE CASCADE,
    intencao VARCHAR(100) NOT NULL, -- 'justificar_atraso', 'alterar_horario', 'solicitar_relatorio', etc.
    confianca DECIMAL(5,2) CHECK (confianca BETWEEN 0 AND 100), -- Nível de confiança da detecção (0-100)
    entidades JSONB, -- Entidades extraídas da mensagem (nomes, datas, horários, etc.)
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela para conversas de alteração de horário
CREATE TABLE conversas_alteracao_horario (
    id SERIAL PRIMARY KEY,
    conversa_id INTEGER REFERENCES conversas_whatsapp(id) ON DELETE CASCADE,
    estado VARCHAR(50) NOT NULL CHECK (estado IN ('coletando_info', 'confirmando', 'finalizado', 'cancelado', 'erro')),
    dados_coletados JSONB, -- Dados já coletados
    informacao_pendente VARCHAR(100), -- O que o agente está esperando receber
    alteracao_id INTEGER REFERENCES alteracoes_horario(id) ON DELETE SET NULL, -- Referência à alteração criada
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela para estado global do sistema
CREATE TABLE configuracoes_sistema (
    id SERIAL PRIMARY KEY,
    chave VARCHAR(100) UNIQUE NOT NULL,
    valor TEXT,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('texto', 'numero', 'booleano', 'json', 'data', 'hora')),
    descricao TEXT,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_por VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela para log de operações do sistema
CREATE TABLE log_sistema (
    id SERIAL PRIMARY KEY,
    operacao VARCHAR(100) NOT NULL,
    usuario VARCHAR(100),
    detalhes JSONB,
    status VARCHAR(20) NOT NULL CHECK (status IN ('sucesso', 'erro', 'aviso', 'info')),
    ip VARCHAR(45),
    user_agent TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- TRIGGERS E FUNÇÕES
-- =============================================

-- Função para atualizar o campo updated_at (usada por vários triggers)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Função para atualizar o campo atualizado_em (usada pelas tabelas de banco de horas)
CREATE OR REPLACE FUNCTION update_atualizado_em()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para atualizar o campo updated_at automaticamente
CREATE TRIGGER update_secretarias_modtime BEFORE UPDATE ON secretarias
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_servidores_modtime BEFORE UPDATE ON servidores
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_horarios_padrao_modtime BEFORE UPDATE ON horarios_padrao
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alteracoes_horario_modtime BEFORE UPDATE ON alteracoes_horario
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_feriados_modtime BEFORE UPDATE ON feriados
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_batidas_processadas_modtime BEFORE UPDATE ON batidas_processadas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_justificativas_modtime BEFORE UPDATE ON justificativas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_relatorios_modtime BEFORE UPDATE ON relatorios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contatos_whatsapp_modtime BEFORE UPDATE ON contatos_whatsapp
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversas_whatsapp_modtime BEFORE UPDATE ON conversas_whatsapp
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversas_alteracao_horario_modtime BEFORE UPDATE ON conversas_alteracao_horario
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_configuracoes_sistema_modtime BEFORE UPDATE ON configuracoes_sistema
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Função para atualizar última interação do contato quando uma mensagem é criada
CREATE OR REPLACE FUNCTION atualizar_ultima_interacao_contato()
RETURNS TRIGGER AS $$
BEGIN
    -- Atualiza a última interação da conversa
    UPDATE conversas_whatsapp 
    SET ultima_interacao = NEW.criado_em
    WHERE id = NEW.conversa_id;
    
    -- Atualiza a última interação do contato
    UPDATE contatos_whatsapp 
    SET ultima_interacao = NEW.criado_em
    WHERE id = (SELECT contato_id FROM conversas_whatsapp WHERE id = NEW.conversa_id);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER atualizar_interacao_apos_mensagem
AFTER INSERT ON mensagens_whatsapp
FOR EACH ROW EXECUTE FUNCTION atualizar_ultima_interacao_contato();

-- Função para calcular a carga horária diária automaticamente
CREATE OR REPLACE FUNCTION calcular_carga_horaria_diaria()
RETURNS TRIGGER AS $$
DECLARE
    tempo_1 interval;
    tempo_2 interval;
BEGIN
    -- Calcular período da manhã/primeiro período
    IF NEW.entrada_1 IS NOT NULL AND NEW.saida_1 IS NOT NULL THEN
        tempo_1 := NEW.saida_1 - NEW.entrada_1;
    ELSE
        tempo_1 := interval '0';
    END IF;
    
    -- Calcular período da tarde/segundo período
    IF NEW.entrada_2 IS NOT NULL AND NEW.saida_2 IS NOT NULL THEN
        tempo_2 := NEW.saida_2 - NEW.entrada_2;
    ELSE
        tempo_2 := interval '0';
    END IF;
    
    -- Somar os dois períodos
    NEW.carga_horaria_diaria := tempo_1 + tempo_2;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger no horário padrão
CREATE TRIGGER calcular_carga_horaria_padrao
BEFORE INSERT OR UPDATE ON horarios_padrao
FOR EACH ROW EXECUTE FUNCTION calcular_carga_horaria_diaria();

-- Aplicar trigger nas alterações de horário
CREATE TRIGGER calcular_carga_horaria_alteracao
BEFORE INSERT OR UPDATE ON alteracoes_horario
FOR EACH ROW EXECUTE FUNCTION calcular_carga_horaria_diaria();

-- Função para finalizar conversa automaticamente após período de inatividade
CREATE OR REPLACE FUNCTION verificar_conversas_inativas()
RETURNS void AS $$
DECLARE
    tempo_limite interval;
BEGIN
    -- Obter o tempo limite das configurações do sistema (padrão 24 horas)
    SELECT COALESCE(valor::interval, interval '24 hours') INTO tempo_limite
    FROM configuracoes_sistema 
    WHERE chave = 'tempo_inatividade_conversa';

    -- Finalizar conversas inativas
    UPDATE conversas_whatsapp
    SET 
        status = 'finalizada',
        finalizada_em = CURRENT_TIMESTAMP,
        resultado_acao = 'Finalizada automaticamente por inatividade'
    WHERE 
        status = 'ativa' AND
        CURRENT_TIMESTAMP - ultima_interacao > tempo_limite;
END;
$$ LANGUAGE plpgsql;

-- Função para criar log de alterações em justificativas
CREATE OR REPLACE FUNCTION log_alteracoes_justificativa()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        IF OLD.status <> NEW.status THEN
            INSERT INTO log_sistema (
                operacao, 
                usuario, 
                detalhes,
                status
            ) VALUES (
                'alteracao_status_justificativa',
                NEW.aprovado_por,
                jsonb_build_object(
                    'justificativa_id', NEW.id,
                    'servidor_id', NEW.servidor_id,
                    'status_anterior', OLD.status,
                    'status_novo', NEW.status,
                    'data_justificativa', NEW.data
                ),
                'sucesso'
            );
        END IF;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER log_alteracoes_justificativa_after
AFTER UPDATE ON justificativas
FOR EACH ROW EXECUTE FUNCTION log_alteracoes_justificativa();

-- Função para validar e processar novas batidas
CREATE OR REPLACE FUNCTION processar_nova_batida()
RETURNS TRIGGER AS $$
DECLARE
    v_ultima_batida batidas_originais%ROWTYPE;
    v_status varchar;
BEGIN
    -- Buscar a última batida do servidor
    SELECT * INTO v_ultima_batida
    FROM batidas_originais
    WHERE servidor_id = NEW.servidor_id
      AND data_hora < NEW.data_hora
    ORDER BY data_hora DESC
    LIMIT 1;
    
    -- Verificar se é uma sequência válida de entrada/saída
    IF v_ultima_batida IS NULL OR v_ultima_batida.tipo <> NEW.tipo THEN
        v_status := 'normal';
    ELSE
        v_status := 'inconsistente';
    END IF;
    
    -- Inserir na tabela de processadas
    INSERT INTO batidas_processadas (
        batida_original_id,
        servidor_id,
        data_hora,
        tipo,
        status,
        processado_em
    ) VALUES (
        NEW.id,
        NEW.servidor_id,
        NEW.data_hora,
        NEW.tipo,
        v_status,
        CURRENT_TIMESTAMP
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER processar_batida_after_insert
AFTER INSERT ON batidas_originais
FOR EACH ROW EXECUTE FUNCTION processar_nova_batida();

-- Função para criar automaticamente conversas de alteração específicas
CREATE OR REPLACE FUNCTION iniciar_conversa_alteracao()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.tipo = 'alteracao_horario' THEN
        INSERT INTO conversas_alteracao_horario (
            conversa_id,
            estado,
            dados_coletados,
            informacao_pendente,
            criado_em,
            atualizado_em
        ) VALUES (
            NEW.id,
            'coletando_info',
            jsonb_build_object('tipo', 'alteracao_horario'),
            'secretaria_ou_servidor',
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER iniciar_conversa_alteracao_after_insert
AFTER INSERT ON conversas_whatsapp
FOR EACH ROW EXECUTE FUNCTION iniciar_conversa_alteracao();

-- Função para registrar automaticamente a intenção detectada em uma mensagem
CREATE OR REPLACE FUNCTION registrar_intencao_de_audio()
RETURNS TRIGGER AS $$
BEGIN
    -- Se for uma mensagem de áudio que foi transcrita
    IF NEW.tipo_midia = 'audio' AND NEW.conteudo IS NOT NULL AND NEW.conteudo <> '[Processando áudio...]' AND NEW.direcao = 'entrada' THEN
        -- Inserir uma entrada na tabela de intenções
        INSERT INTO intencoes_conversa (
            mensagem_id,
            intencao,
            confianca,
            entidades,
            criado_em
        ) VALUES (
            NEW.id,
            'pendente_analise', -- Será processado pelo sistema NLP depois
            0.0, -- Confiança inicial zero
            '{}'::jsonb, -- Entidades vazias inicialmente
            CURRENT_TIMESTAMP
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER analisar_audio_apos_transcricao
AFTER UPDATE ON mensagens_whatsapp
FOR EACH ROW
WHEN (OLD.conteudo = '[Processando áudio...]' AND NEW.conteudo <> '[Processando áudio...]')
EXECUTE FUNCTION registrar_intencao_de_audio();

-- Função para atualizar justificativa quando aprovada
CREATE OR REPLACE FUNCTION atualizar_batidas_apos_justificativa()
RETURNS TRIGGER AS $$
BEGIN
    -- Se a justificativa foi aprovada
    IF NEW.status = 'aprovada' AND OLD.status <> 'aprovada' THEN
        -- Atualizar as batidas relacionadas
        UPDATE batidas_processadas
        SET 
            status = 'justificada',
            justificativa_id = NEW.id,
            updated_at = CURRENT_TIMESTAMP
        WHERE 
            servidor_id = NEW.servidor_id AND
            DATE(data_hora) = NEW.data AND
            status = 'inconsistente';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER justificativa_aprovada_after_update
AFTER UPDATE ON justificativas
FOR EACH ROW
WHEN (NEW.status = 'aprovada' AND OLD.status <> 'aprovada')
EXECUTE FUNCTION atualizar_batidas_apos_justificativa();

-- =============================================
-- ÍNDICES
-- =============================================

-- Índices para otimização de consultas frequentes
CREATE INDEX idx_servidores_secretaria ON servidores(secretaria_id);
CREATE INDEX idx_servidores_whatsapp ON servidores(whatsapp);
CREATE INDEX idx_servidores_ativo ON servidores(ativo);
CREATE INDEX idx_horarios_padrao_servidor ON horarios_padrao(servidor_id);

CREATE INDEX idx_batidas_originais_servidor ON batidas_originais(servidor_id);
CREATE INDEX idx_batidas_originais_data ON batidas_originais(data_hora);
CREATE INDEX idx_batidas_originais_tipo ON batidas_originais(tipo);

CREATE INDEX idx_batidas_processadas_servidor ON batidas_processadas(servidor_id);
CREATE INDEX idx_batidas_processadas_data ON batidas_processadas(data_hora);
CREATE INDEX idx_batidas_processadas_status ON batidas_processadas(status);
CREATE INDEX idx_batidas_processadas_tipo ON batidas_processadas(tipo);

CREATE INDEX idx_justificativas_servidor ON justificativas(servidor_id);
CREATE INDEX idx_justificativas_data ON justificativas(data);
CREATE INDEX idx_justificativas_status ON justificativas(status);

CREATE INDEX idx_alteracoes_periodo ON alteracoes_horario(data_inicio, data_fim);
CREATE INDEX idx_alteracoes_ativo ON alteracoes_horario(ativo);

CREATE INDEX idx_alteracoes_servidor ON alteracoes_horario_servidores(servidor_id);
CREATE INDEX idx_alteracoes_secretaria ON alteracoes_horario_secretarias(secretaria_id);

CREATE INDEX idx_mensagens_conversa ON mensagens_whatsapp(conversa_id);
CREATE INDEX idx_mensagens_criacao ON mensagens_whatsapp(criado_em);
CREATE INDEX idx_mensagens_processado ON mensagens_whatsapp(processado);
CREATE INDEX idx_mensagens_tipo_midia ON mensagens_whatsapp(tipo_midia);

CREATE INDEX idx_conversas_contato ON conversas_whatsapp(contato_id);
CREATE INDEX idx_conversas_status ON conversas_whatsapp(status);
CREATE INDEX idx_conversas_tipo ON conversas_whatsapp(tipo);
CREATE INDEX idx_conversas_data ON conversas_whatsapp(iniciada_em);

CREATE INDEX idx_contatos_servidor ON contatos_whatsapp(servidor_id);
CREATE INDEX idx_contatos_secretaria ON contatos_whatsapp(secretaria_id);
CREATE INDEX idx_contatos_gestor ON contatos_whatsapp(is_gestor);

CREATE INDEX idx_intencoes_mensagem ON intencoes_conversa(mensagem_id);
CREATE INDEX idx_intencoes_tipo ON intencoes_conversa(intencao);

CREATE INDEX idx_feriados_data ON feriados(data);
CREATE INDEX idx_feriados_tipo ON feriados(tipo);

-- Índices para consultas por período
CREATE INDEX idx_relatorios_periodo ON relatorios(periodo_inicio, periodo_fim);
CREATE INDEX idx_relatorios_tipo ON relatorios(tipo);

-- Índice para buscas textuais em comandos
CREATE INDEX idx_comandos_texto ON log_comandos_naturais USING gin(to_tsvector('portuguese', comando));

-- Índice para buscas em configurações
CREATE INDEX idx_configuracoes_chave ON configuracoes_sistema(chave);

-- Índice para logs do sistema
CREATE INDEX idx_logs_operacao ON log_sistema(operacao);
CREATE INDEX idx_logs_data ON log_sistema(criado_em);
CREATE INDEX idx_logs_status ON log_sistema(status);

-- =============================================
-- VISÕES
-- =============================================

-- Visão para consulta rápida de horas trabalhadas por dia
-- Continuação da visão vw_horas_trabalhadas_dia
CREATE OR REPLACE VIEW vw_horas_trabalhadas_dia AS
SELECT 
    servidor_id,
    DATE(b1.data_hora) AS data,
    MIN(CASE WHEN b1.tipo = 'entrada' THEN b1.data_hora END) AS primeira_entrada,
    MAX(CASE WHEN b1.tipo = 'saida' THEN b1.data_hora END) AS ultima_saida,
    COUNT(b1.id) AS total_batidas,
    EXTRACT(EPOCH FROM (MAX(CASE WHEN b1.tipo = 'saida' THEN b1.data_hora END) - 
                       MIN(CASE WHEN b1.tipo = 'entrada' THEN b1.data_hora END)))/3600 AS horas_trabalhadas
FROM 
    batidas_processadas b1
WHERE 
    b1.status IN ('normal', 'justificada')
GROUP BY 
    servidor_id, DATE(b1.data_hora);

-- Visão para consulta de situação dos servidores em determinada data
CREATE OR REPLACE VIEW vw_situacao_diaria_servidores AS
SELECT 
    s.id AS servidor_id,
    s.nome AS servidor_nome,
    s.matricula,
    sec.nome AS secretaria,
    d.data,
    CASE 
        WHEN f.id IS NOT NULL THEN 'feriado'
        WHEN EXTRACT(DOW FROM d.data) IN (0, 6) THEN 'fim_de_semana'
        WHEN j.id IS NOT NULL AND j.status = 'aprovada' AND j.tipo = 'falta' THEN 'falta_justificada'
        WHEN ht.horas_trabalhadas IS NULL THEN 'ausente'
        WHEN ht.horas_trabalhadas < EXTRACT(EPOCH FROM hp.carga_horaria_diaria)/3600 THEN 'horas_insuficientes'
        ELSE 'presente'
    END AS situacao,
    COALESCE(ht.horas_trabalhadas, 0) AS horas_trabalhadas,
    EXTRACT(EPOCH FROM COALESCE(hp.carga_horaria_diaria, '08:00:00'::interval))/3600 AS carga_horaria_esperada
FROM 
    servidores s
CROSS JOIN 
    (SELECT generate_series(CURRENT_DATE - 30, CURRENT_DATE, '1 day'::interval)::date AS data) d
LEFT JOIN 
    secretarias sec ON s.secretaria_id = sec.id
LEFT JOIN 
    feriados f ON d.data = f.data AND f.ativo = true
LEFT JOIN 
    horarios_padrao hp ON s.id = hp.servidor_id AND EXTRACT(DOW FROM d.data) = hp.dia_semana
LEFT JOIN 
    vw_horas_trabalhadas_dia ht ON s.id = ht.servidor_id AND d.data = ht.data
LEFT JOIN 
    justificativas j ON s.id = j.servidor_id AND d.data = j.data
WHERE 
    s.ativo = true AND
    (s.data_demissao IS NULL OR s.data_demissao >= d.data) AND
    s.data_admissao <= d.data
ORDER BY 
    d.data DESC, sec.nome, s.nome;

-- Visão para inconsistências recentes
CREATE OR REPLACE VIEW vw_inconsistencias_recentes AS
SELECT 
    s.id AS servidor_id,
    s.nome AS servidor_nome,
    s.matricula,
    sec.nome AS secretaria,
    bp.data_hora,
    bp.tipo,
    bp.status,
    j.id AS justificativa_id,
    j.status AS status_justificativa
FROM 
    batidas_processadas bp
JOIN 
    servidores s ON bp.servidor_id = s.id
LEFT JOIN 
    secretarias sec ON s.secretaria_id = sec.id
LEFT JOIN 
    justificativas j ON bp.justificativa_id = j.id
WHERE 
    bp.status = 'inconsistente' AND
    bp.data_hora >= CURRENT_DATE - 30
ORDER BY 
    bp.data_hora DESC;

-- Visão para estatísticas de conversas WhatsApp
CREATE OR REPLACE VIEW vw_estatisticas_whatsapp AS
SELECT 
    DATE(cw.iniciada_em) AS data,
    cw.tipo,
    COUNT(cw.id) AS total_conversas,
    AVG(EXTRACT(EPOCH FROM (COALESCE(cw.finalizada_em, CURRENT_TIMESTAMP) - cw.iniciada_em))/60) AS duracao_media_minutos,
    COUNT(CASE WHEN cw.status = 'finalizada' AND cw.resultado_acao IS NOT NULL THEN 1 END) AS conversas_concluidas_sucesso,
    COUNT(CASE WHEN cw.status = 'finalizada' AND cw.resultado_acao IS NULL THEN 1 END) AS conversas_concluidas_sem_acao,
    COUNT(CASE WHEN cw.status = 'cancelada' THEN 1 END) AS conversas_canceladas,
    COUNT(CASE WHEN cw.status = 'ativa' THEN 1 END) AS conversas_ativas
FROM 
    conversas_whatsapp cw
WHERE 
    cw.iniciada_em >= CURRENT_DATE - 30
GROUP BY 
    DATE(cw.iniciada_em), cw.tipo
ORDER BY 
    data DESC, cw.tipo;

-- =============================================
-- MÓDULO DE BANCO DE HORAS (COMENTADO)
-- =============================================
-- Esta seção foi comentada pois faz referência a tabelas que não existem no esquema atual.
-- Para ativar esse módulo, seria necessário criar as tabelas 'funcionarios' e 'banco_horas' primeiro.

/*
-- Tabela para definir políticas de banco de horas
CREATE TABLE politicas_banco_horas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    max_diario_normal INTEGER, -- Limite em minutos (NULL = sem limite)
    max_diario_feriado INTEGER, -- Limite em minutos (NULL = sem limite)
    max_diario_fds INTEGER, -- Limite em minutos para fins de semana (NULL = sem limite)
    max_semanal INTEGER, -- Limite em minutos (NULL = sem limite)
    max_mensal INTEGER, -- Limite em minutos (NULL = sem limite)
    permitir_negativo BOOLEAN DEFAULT TRUE, -- Se pode ficar negativo no banco
    requer_aprovacao BOOLEAN DEFAULT FALSE, -- Se requer aprovação para acumular
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela para atribuir políticas a funcionários
CREATE TABLE funcionario_politica_banco_horas (
    id SERIAL PRIMARY KEY,
    funcionario_id INTEGER REFERENCES funcionarios(id) ON DELETE CASCADE,
    politica_id INTEGER REFERENCES politicas_banco_horas(id) ON DELETE RESTRICT,
    data_inicio DATE NOT NULL,
    data_fim DATE, -- NULL indica sem data fim
    observacao TEXT,
    autorizado_por INTEGER REFERENCES funcionarios(id),
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (funcionario_id, data_inicio) -- Evita sobreposição
);

-- Adicionar um campo na tabela de banco_horas para verificar se a hora foi autorizada
ALTER TABLE banco_horas 
ADD COLUMN autorizado BOOLEAN DEFAULT FALSE,
ADD COLUMN autorizado_por INTEGER REFERENCES funcionarios(id),
ADD COLUMN data_autorizacao TIMESTAMP WITH TIME ZONE;

-- Tabela para registro de autorizações específicas (exceções)
CREATE TABLE autorizacoes_horas_extras (
    id SERIAL PRIMARY KEY,
    funcionario_id INTEGER REFERENCES funcionarios(id) NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    motivo TEXT NOT NULL,
    limite_diario INTEGER, -- Em minutos, NULL = sem limite
    autorizado_por INTEGER REFERENCES funcionarios(id) NOT NULL,
    observacoes TEXT,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Inserir políticas padrão
INSERT INTO politicas_banco_horas 
(nome, descricao, max_diario_normal, max_diario_feriado, max_diario_fds, max_semanal, max_mensal, permitir_negativo, requer_aprovacao) 
VALUES 
('Sem Restrições', 'Sem limites para banco de horas', NULL, NULL, NULL, NULL, NULL, TRUE, FALSE),
('Padrão', 'Até 2h por dia normal, 8h em feriados/fins de semana, máximo de 20h/mês', 120, 480, 480, 600, 1200, TRUE, FALSE),
('Restrito', 'Até 1h por dia normal, 4h em feriados/fins de semana, máximo de 10h/mês, requer aprovação', 60, 240, 240, 300, 600, TRUE, TRUE),
('Sem Banco de Horas', 'Não permite acúmulo de banco de horas', 0, 0, 0, 0, 0, FALSE, TRUE);

-- Função para verificar se hora extra está dentro dos limites de política
CREATE OR REPLACE FUNCTION verificar_permissao_hora_extra(
    p_funcionario_id INTEGER,
    p_data DATE,
    p_minutos INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    v_politica_id INTEGER;
    v_max_diario INTEGER;
    v_max_semanal INTEGER;
    v_max_mensal INTEGER;
    v_total_diario INTEGER;
    v_total_semanal INTEGER;
    v_total_mensal INTEGER;
    v_autorizacao_especial BOOLEAN := FALSE;
    v_eh_feriado BOOLEAN;
    v_eh_fds BOOLEAN;
BEGIN
    -- Verifica se é feriado
    SELECT EXISTS(SELECT 1 FROM feriados WHERE data = p_data) INTO v_eh_feriado;
    
    -- Verifica se é fim de semana
    v_eh_fds := EXTRACT(DOW FROM p_data) IN (0, 6); -- 0=domingo, 6=sábado
    
    -- Busca política vigente do funcionário
    SELECT politica_id INTO v_politica_id
    FROM funcionario_politica_banco_horas
    WHERE funcionario_id = p_funcionario_id
    AND p_data BETWEEN data_inicio AND COALESCE(data_fim, '9999-12-31'::DATE)
    ORDER BY data_inicio DESC
    LIMIT 1;
    
    -- Se não tem política definida, usa a padrão (id=2)
    IF v_politica_id IS NULL THEN
        v_politica_id := 2; -- ID da política 'Padrão'
    END IF;
    
    -- Verifica se tem autorização especial para a data
    SELECT EXISTS(
        SELECT 1 
        FROM autorizacoes_horas_extras 
        WHERE funcionario_id = p_funcionario_id
        AND p_data BETWEEN data_inicio AND data_fim
    ) INTO v_autorizacao_especial;
    
    -- Se tem autorização especial, busca o limite especial
    IF v_autorizacao_especial THEN
        SELECT limite_diario INTO v_max_diario
        FROM autorizacoes_horas_extras
        WHERE funcionario_id = p_funcionario_id
        AND p_data BETWEEN data_inicio AND data_fim
        ORDER BY data_inicio DESC
        LIMIT 1;
        
        -- Se limite não for definido, consideramos sem limite
        IF v_max_diario IS NULL THEN
            RETURN TRUE;
        END IF;
    ELSE
        -- Determina o limite com base no tipo de dia
        IF v_eh_feriado THEN
            SELECT max_diario_feriado INTO v_max_diario
            FROM politicas_banco_horas
            WHERE id = v_politica_id;
        ELSIF v_eh_fds THEN
            SELECT max_diario_fds INTO v_max_diario
            FROM politicas_banco_horas
            WHERE id = v_politica_id;
        ELSE
            SELECT max_diario_normal INTO v_max_diario
            FROM politicas_banco_horas
            WHERE id = v_politica_id;
        END IF;
        
        -- Também obtém limites semanal e mensal
        SELECT max_semanal, max_mensal 
        INTO v_max_semanal, v_max_mensal
        FROM politicas_banco_horas
        WHERE id = v_politica_id;
    END IF;
    
    -- Se não tem limite diário, verifica semanal e mensal
    IF v_max_diario IS NULL THEN
        -- Verifica limites semanal e mensal se forem definidos
        IF v_max_semanal IS NOT NULL OR v_max_mensal IS NOT NULL THEN
            -- Total acumulado na semana atual
            SELECT COALESCE(SUM(credito), 0) INTO v_total_semanal
            FROM banco_horas
            WHERE funcionario_id = p_funcionario_id
            AND data BETWEEN 
                p_data - EXTRACT(DOW FROM p_data)::INTEGER 
                AND p_data;
                
            -- Total acumulado no mês atual
            SELECT COALESCE(SUM(credito), 0) INTO v_total_mensal
            FROM banco_horas
            WHERE funcionario_id = p_funcionario_id
            AND EXTRACT(MONTH FROM data) = EXTRACT(MONTH FROM p_data)
            AND EXTRACT(YEAR FROM data) = EXTRACT(YEAR FROM p_data);
            
            -- Verifica se excede limites
            IF v_max_semanal IS NOT NULL AND (v_total_semanal + p_minutos) > v_max_semanal THEN
                RETURN FALSE;
            END IF;
            
            IF v_max_mensal IS NOT NULL AND (v_total_mensal + p_minutos) > v_max_mensal THEN
                RETURN FALSE;
            END IF;
        END IF;
        
        -- Se passou pelas verificações ou não tem limites definidos
        RETURN TRUE;
    END IF;
    
    -- Total já acumulado no dia
    SELECT COALESCE(SUM(credito), 0) INTO v_total_diario
    FROM banco_horas
    WHERE funcionario_id = p_funcionario_id
    AND data = p_data;
    
    -- Verifica se ultrapassaria o limite diário
    IF (v_total_diario + p_minutos) > v_max_diario THEN
        RETURN FALSE;
    END IF;
    
    -- Se passou por todas as verificações, está permitido
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Trigger para verificar limites de horas extras antes de inserir
CREATE OR REPLACE FUNCTION verificar_limites_banco_horas()
RETURNS TRIGGER AS $$
DECLARE
    v_permitido BOOLEAN;
    v_requer_aprovacao BOOLEAN;
BEGIN
    -- Se não tem crédito, não precisa verificar
    IF NEW.credito <= 0 THEN
        RETURN NEW;
    END IF;
    
    -- Verifica se está dentro dos limites de política
    SELECT verificar_permissao_hora_extra(NEW.funcionario_id, NEW.data, NEW.credito)
    INTO v_permitido;
    
    -- Verifica se requer aprovação
    SELECT requer_aprovacao INTO v_requer_aprovacao
    FROM politicas_banco_horas p
    JOIN funcionario_politica_banco_horas fp ON p.id = fp.politica_id
    WHERE fp.funcionario_id = NEW.funcionario_id
    AND NEW.data BETWEEN fp.data_inicio AND COALESCE(fp.data_fim, '9999-12-31'::DATE)
    ORDER BY fp.data_inicio DESC
    LIMIT 1;
    
    -- Se não encontrou política específica, usa a padrão
    IF v_requer_aprovacao IS NULL THEN
        SELECT requer_aprovacao INTO v_requer_aprovacao
        FROM politicas_banco_horas
        WHERE id = 2; -- ID da política 'Padrão'
    END IF;
    
    -- Define se está autorizado com base na política e nos limites
    IF v_permitido AND NOT COALESCE(v_requer_aprovacao, FALSE) THEN
        NEW.autorizado := TRUE;
    ELSE
        NEW.autorizado := FALSE;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_verificar_limites_banco_horas
BEFORE INSERT OR UPDATE ON banco_horas
FOR EACH ROW
EXECUTE FUNCTION verificar_limites_banco_horas();

-- Trigger para o campo updated_at na tabela
CREATE TRIGGER update_funcionario_politica_banco_horas_atualizado_em
BEFORE UPDATE ON funcionario_politica_banco_horas
FOR EACH ROW
EXECUTE FUNCTION update_atualizado_em();

CREATE TRIGGER update_politicas_banco_horas_atualizado_em
BEFORE UPDATE ON politicas_banco_horas
FOR EACH ROW
EXECUTE FUNCTION update_atualizado_em();

CREATE TRIGGER update_autorizacoes_horas_extras_atualizado_em
BEFORE UPDATE ON autorizacoes_horas_extras
FOR EACH ROW
EXECUTE FUNCTION update_atualizado_em();
*/
	
	
	
	