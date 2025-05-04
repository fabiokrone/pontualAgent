-- Dados iniciais
-- Script para popular o banco de dados com dados iniciais
-- Salvar como docker/postgres/populate_initial_data.sql

-- Populando Secretarias
INSERT INTO ponto.secretarias (nome, codigo, ativo)
VALUES 
    ('Secretaria Municipal de Administração e Finanças', 'SEMAF', true),
    ('Secretaria Municipal de Educação e Cultura', 'SEMEC', true);

-- Populando Servidores
INSERT INTO ponto.servidores (
    matricula, nome, email, telefone, whatsapp, 
    secretaria_id, cargo, ativo, data_admissao, cpf
)
VALUES 
    ('4832', 'Fábio Krone', 'fabiokrone10@gmail.com', '49999606220', '49999606220', 
     1, 'Diretor de RH', true, '2025-01-02', '12345678900'),
    ('3344', 'Marcos Vinícius Redel', 'marcos_redel@hotmail.com', '49991385226', '49991385226', 
     1, 'Contador', true, '2016-01-11', '98765432100');

-- Populando Horários Padrão
-- Horário para dias úteis (segunda a sexta, dias 1-5) para o servidor Fábio
INSERT INTO ponto.horarios_padrao (
    servidor_id, dia_semana, entrada_1, saida_1, entrada_2, saida_2
)
SELECT 
    s.id, dia.dia_semana, '07:30:00'::time, '11:30:00'::time, '13:30:00'::time, '17:30:00'::time
FROM 
    ponto.servidores s,
    (SELECT generate_series(1, 5) AS dia_semana) dia
WHERE 
    s.matricula = '4832';

-- Horário para dias úteis (segunda a sexta, dias 1-5) para o servidor Marcos
INSERT INTO ponto.horarios_padrao (
    servidor_id, dia_semana, entrada_1, saida_1, entrada_2, saida_2
)
SELECT 
    s.id, dia.dia_semana, '07:30:00'::time, '11:30:00'::time, '13:00:00'::time, '17:00:00'::time
FROM 
    ponto.servidores s,
    (SELECT generate_series(1, 5) AS dia_semana) dia
WHERE 
    s.matricula = '3344';

-- Feriados para 2025
INSERT INTO ponto.feriados (data, descricao, tipo, ambito)
VALUES
    ('2025-01-01', 'Confraternização Universal', 'feriado', 'nacional'),
    ('2025-03-03', 'Carnaval', 'feriado', 'nacional'),
    ('2025-03-04', 'Carnaval', 'feriado', 'nacional'),
    ('2025-04-18', 'Paixão de Cristo', 'feriado', 'nacional'),
    ('2025-04-21', 'Tiradentes', 'feriado', 'nacional'),
    ('2025-05-01', 'Dia do Trabalho', 'feriado', 'nacional'),
    ('2025-06-19', 'Corpus Christi', 'ponto_facultativo', 'nacional'),
    ('2025-09-07', 'Independência do Brasil', 'feriado', 'nacional'),
    ('2025-10-12', 'Nossa Senhora Aparecida - Padroeira do Brasil', 'feriado', 'nacional'),
    ('2025-11-02', 'Finados', 'feriado', 'nacional'),
    ('2025-11-15', 'Proclamação da República', 'feriado', 'nacional'),
    ('2025-11-20', 'Dia Nacional de Zumbi e da Consciência Negra', 'feriado', 'nacional'),
    ('2025-12-25', 'Natal', 'feriado', 'nacional');

-- Populando Usuários para autenticação
--INSERT INTO ponto.usuarios (
--    username, email, nome_completo, senha_hash, 
--    ativo, perfil, secretaria_id, servidor_id
--)
--VALUES 
--    ('admin', 'admin@pontual.com', 'Administrador do Sistema', 
--     '$2b$12$tPFU4xCPF3xNYRuq0nU.MOXYDpQJKdZaQZaJmQYQ.Jnpui/i/o0TK', -- Senha: admin123
--     true, 'admin', 1, NULL),
--    ('fabio', 'fabiokrone10@gmail.com', 'Fábio Krone', 
--     '$2b$12$tPFU4xCPF3xNYRuq0nU.MOXYDpQJKdZaQZaJmQYQ.Jnpui/i/o0TK', -- Senha: admin123
--     true, 'gestor', 1, (SELECT id FROM ponto.servidores WHERE matricula = '4832')),
--    ('marcos', 'marcos_redel@hotmail.com', 'Marcos Vinícius Redel', 
--     '$2b$12$tPFU4xCPF3xNYRuq0nU.MOXYDpQJKdZaQZaJmQYQ.Jnpui/i/o0TK', -- Senha: admin123
--     true, 'usuario', 1, (SELECT id FROM ponto.servidores WHERE matricula = '3344'));