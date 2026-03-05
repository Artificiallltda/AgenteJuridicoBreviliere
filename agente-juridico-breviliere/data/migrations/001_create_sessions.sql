-- Migration: Criação da tabela de sessões para persistência de conversas
-- Breviliere Advocacia — Sprint 2

CREATE TABLE IF NOT EXISTS sessions (
    session_id  VARCHAR(255) PRIMARY KEY,
    channel     VARCHAR(50)  NOT NULL,
    state_json  JSONB        NOT NULL,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Índice para buscas por data (usado no cleanup de sessões expiradas)
CREATE INDEX IF NOT EXISTS idx_sessions_updated_at ON sessions(updated_at);

-- Tabela de logs de uso do LLM (tracking de tokens e custo)
CREATE TABLE IF NOT EXISTS usage_logs (
    id          SERIAL       PRIMARY KEY,
    session_id  VARCHAR(255),
    model       VARCHAR(100) NOT NULL,
    tokens_used INTEGER      NOT NULL DEFAULT 0,
    latency_ms  FLOAT        NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Índice para análise por period
CREATE INDEX IF NOT EXISTS idx_usage_logs_created_at ON usage_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_usage_logs_session ON usage_logs(session_id);

-- Comentários
COMMENT ON TABLE sessions IS 'Persistência de estado das conversas do bot Breviliere';
COMMENT ON TABLE usage_logs IS 'Rastreamento de tokens e custo por conversa';
COMMENT ON COLUMN sessions.state_json IS 'ConversationState serializado como JSON';
