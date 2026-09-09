-- ============================================================
-- NEWFLOW - ESTRUTURA DO BANCO DE DADOS
-- ============================================================

-- ============================================================
-- TABELA: usuarios
-- Armazena os dados de acesso dos usuários
-- ============================================================

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- TABELA: perfis_musicais
-- Armazena o gosto musical de cada usuário
-- ============================================================

CREATE TABLE perfis_musicais (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL UNIQUE,

    generos TEXT,
    artistas TEXT,
    musicas_favoritas TEXT,
    humor_preferido TEXT,
    decadas_preferidas TEXT,

    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_perfil_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
);


-- ============================================================
-- TABELA: recomendacoes
-- Armazena as músicas recomendadas pelo NewFlow
-- ============================================================

CREATE TABLE recomendacoes (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL,

    musica VARCHAR(200) NOT NULL,
    artista VARCHAR(200) NOT NULL,
    motivo TEXT,

    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_recomendacao_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE
);


-- ============================================================
-- TABELA: feedbacks
-- Armazena a avaliação do usuário sobre uma recomendação
-- ============================================================

CREATE TABLE feedbacks (
    id SERIAL PRIMARY KEY,

    usuario_id INTEGER NOT NULL,
    recomendacao_id INTEGER NOT NULL,

    tipo VARCHAR(20) NOT NULL,

    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_feedback_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_feedback_recomendacao
        FOREIGN KEY (recomendacao_id)
        REFERENCES recomendacoes(id)
        ON DELETE CASCADE,

    CONSTRAINT check_tipo_feedback
        CHECK (tipo IN ('curti', 'nao_curti'))
);


-- ============================================================
-- FIM DO SCHEMA
-- ============================================================