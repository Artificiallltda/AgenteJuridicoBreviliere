# Guia de Estrutura e Implementação — Agente Jurídico Breviliere

> **Para o agente AIOS**: Este documento descreve a estrutura completa do projeto, stack tecnológico, padrões de código e ordem de implementação. Use-o como referência principal para construir o sistema.

---

## 1. Estrutura de Pastas Completa

```
agente-juridico-breviliere/
│
├── docs/
│   ├── prd/
│   │   └── PRD.md                         # Product Requirements Document
│   └── architecture/
│       └── STRUCTURE-GUIDE.md             # Este arquivo
│
├── src/
│   ├── main.py                            # Entry point FastAPI
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py                    # Pydantic Settings (.env → tipado)
│   │   └── logging.py                     # structlog config
│   │
│   ├── channels/                          # Adaptadores de canal (Ports)
│   │   ├── __init__.py
│   │   ├── base.py                        # ABC: ChannelAdapter
│   │   ├── whatsapp.py                    # WhatsApp Business API (Meta Cloud API)
│   │   ├── telegram.py                    # Telegram Bot API (python-telegram-bot)
│   │   └── instagram.py                   # Instagram Messaging API
│   │
│   ├── core/                              # Núcleo do agente (Domain)
│   │   ├── __init__.py
│   │   ├── agent.py                       # Orquestrador principal — LangGraph StateMachine
│   │   ├── conversation.py                # Estado da conversa (ConversationState)
│   │   ├── prompts.py                     # System prompts + prompt templates
│   │   ├── personality.py                 # Tom, voz, regras de linguagem
│   │   └── session.py                     # SessionManager (Redis-backed)
│   │
│   ├── triage/                            # Triagem e qualificação de leads
│   │   ├── __init__.py
│   │   ├── questions.py                   # Banco de perguntas por área jurídica
│   │   ├── qualifier.py                   # Motor de qualificação (score 0-100)
│   │   ├── classifier.py                  # Classificador de área (trabalhista, cível, etc.)
│   │   └── flows.py                       # Fluxos adaptativos de triagem (8-12 perguntas)
│   │
│   ├── rag/                               # Pipeline RAG
│   │   ├── __init__.py
│   │   ├── embeddings.py                  # Geração de embeddings (OpenAI/Gemini)
│   │   ├── retriever.py                   # Busca vetorial com filtros de metadados
│   │   ├── indexer.py                     # Indexação e chunking de documentos
│   │   └── chains.py                      # RetrievalQA chains com guardrails
│   │
│   ├── documents/                         # Geração de documentos
│   │   ├── __init__.py
│   │   ├── generator.py                   # Motor de geração (preenche templates)
│   │   ├── pdf_converter.py               # DOCX → PDF (weasyprint)
│   │   └── templates/                     # Templates DOCX editáveis
│   │       ├── proposta_honorarios.docx
│   │       ├── contrato_servicos.docx
│   │       └── briefing.docx
│   │
│   ├── audio/                             # Transcrição de áudio
│   │   ├── __init__.py
│   │   └── transcriber.py                 # OpenAI Whisper API
│   │
│   ├── integrations/                      # Integrações externas
│   │   ├── __init__.py
│   │   ├── crm.py                         # CRM (Pipedrive ou HubSpot)
│   │   ├── pje.py                         # Consulta PJe (MNI/SOAP ou scraping)
│   │   ├── eproc.py                       # Consulta EPROC
│   │   └── notifications.py              # Slack, e-mail, webhook
│   │
│   ├── handoff/                           # Transferência para humano
│   │   ├── __init__.py
│   │   ├── manager.py                     # HandoffManager (transfere + preserva histórico)
│   │   └── queue.py                       # Fila de atendimento humano
│   │
│   ├── models/                            # Modelos de dados (Pydantic + SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── conversation.py                # Conversation, Message, MessageType
│   │   ├── lead.py                        # Lead, LeadScore, LeadStatus
│   │   ├── document.py                    # GeneratedDocument
│   │   └── process.py                     # JudicialProcess, ProcessMovement
│   │
│   ├── database/                          # Persistência
│   │   ├── __init__.py
│   │   ├── connection.py                  # AsyncEngine + sessionmaker (SQLAlchemy async)
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── conversation_repo.py
│   │   │   ├── lead_repo.py
│   │   │   └── document_repo.py
│   │   └── migrations/                    # Alembic
│   │       ├── env.py
│   │       ├── alembic.ini
│   │       └── versions/
│   │
│   └── api/                               # Endpoints REST
│       ├── __init__.py
│       ├── webhooks.py                    # POST /webhook/whatsapp, /webhook/telegram, etc.
│       ├── admin.py                       # GET/POST /admin/knowledge, /admin/leads
│       ├── health.py                      # GET /health, /readiness
│       └── middleware.py                  # CORS, rate limiting, request logging
│
├── knowledge_base/                        # Dados para indexação RAG
│   ├── faq/
│   │   ├── trabalhista.md                 # ~20 perguntas/respostas
│   │   ├── civil.md
│   │   ├── familia.md
│   │   ├── criminal.md
│   │   └── previdenciario.md
│   ├── jurisprudencia/
│   │   ├── sumulas_tst.md
│   │   ├── sumulas_stj.md
│   │   └── README.md
│   ├── templates_texto/
│   │   ├── saudacao.md
│   │   ├── encerramento.md
│   │   ├── lgpd_consent.md
│   │   └── handoff.md
│   └── institucional/
│       ├── areas_atuacao.md
│       ├── equipe.md
│       └── valores_honorarios.md
│
├── tests/
│   ├── conftest.py                        # Fixtures compartilhadas (test DB, mock LLM)
│   ├── unit/
│   │   ├── test_triage_classifier.py
│   │   ├── test_triage_qualifier.py
│   │   ├── test_rag_retriever.py
│   │   ├── test_document_generator.py
│   │   ├── test_audio_transcriber.py
│   │   └── test_handoff_manager.py
│   ├── integration/
│   │   ├── test_whatsapp_webhook.py
│   │   ├── test_telegram_webhook.py
│   │   ├── test_crm_integration.py
│   │   └── test_rag_pipeline.py
│   └── e2e/
│       └── test_full_captacao_flow.py
│
├── scripts/
│   ├── seed_knowledge_base.py             # Indexa knowledge_base/ no vector store
│   ├── setup_dev.sh                       # Setup do ambiente dev (venv, deps, DB)
│   └── test_channels.py                   # Testa conexão com cada canal
│
├── docker/
│   ├── Dockerfile                         # Multi-stage: build + runtime
│   └── docker-compose.yml                 # App + PostgreSQL + Redis + ChromaDB
│
├── .env.example                           # Template de variáveis de ambiente
├── pyproject.toml                         # Configuração do projeto Python
├── requirements.txt                       # Dependências pinadas
├── requirements-dev.txt                   # Dependências de desenvolvimento
└── README.md                              # Documentação do projeto
```

---

## 2. Stack Tecnológico Detalhada

| Camada | Tecnologia | Versão | Justificativa |
|---|---|---|---|
| **Runtime** | Python | 3.12+ | Ecossistema IA maduro, async nativo, tipagem |
| **Framework Web** | FastAPI | 0.110+ | Async, auto-docs OpenAPI, Pydantic nativo |
| **Orquestração LLM** | LangGraph | 0.2+ | StateMachine com estado persistente, fluxos ramificados |
| **LLM Provider** | OpenAI GPT-4o / Gemini 2.0 | latest | Melhor compreensão de PT-BR jurídico |
| **LLM (triagem leve)** | GPT-4o-mini / Gemini Flash | latest | Economia em etapas simples (classificação, extração) |
| **Embeddings** | text-embedding-3-small | latest | Boa relação custo/qualidade para PT-BR |
| **Vector Store** | ChromaDB | dev / Qdrant prod | ChromaDB local p/ dev, Qdrant Cloud em produção |
| **Banco de Dados** | PostgreSQL | 16+ | JSONB, robusto, suporte async (asyncpg) |
| **ORM** | SQLAlchemy | 2.0+ | Async, tipado, Alembic para migrations |
| **Cache/Sessões** | Redis | 7+ | Sessões de conversa, rate limiting, cache |
| **Transcrição** | OpenAI Whisper API | latest | Melhor accuracy PT-BR, streaming |
| **Geração Docs** | python-docx + weasyprint | latest | Templates DOCX, conversão PDF |
| **HTTP Client** | httpx | 0.27+ | Async, timeout, retry built-in |
| **Containerização** | Docker + Compose | latest | Dev/prod consistente |
| **Logs** | structlog | 24+ | JSON estruturado, contexto de sessão |
| **Testes** | pytest + pytest-asyncio | latest | Async, fixtures, parametrize |

---

## 3. Padrões Arquiteturais

### 3.1 Clean Architecture (Onion)

```
┌────────────────────────────────────────────────────────┐
│                    API Layer (api/)                      │
│              Webhooks, Admin, Health                     │
├────────────────────────────────────────────────────────┤
│                 Channels Layer (channels/)               │
│          WhatsApp, Telegram, Instagram                   │
│               ↓ normaliza mensagem ↓                     │
├────────────────────────────────────────────────────────┤
│                  Core Layer (core/)                      │
│       Agent, Conversation, Session, Prompts              │
│               ↓ usa serviços ↓                           │
├────────────────────────────────────────────────────────┤
│              Service Layer (triage/, rag/, etc.)         │
│     Triagem, RAG, Documents, Audio, Handoff              │
├────────────────────────────────────────────────────────┤
│               Data Layer (models/, database/)            │
│        Pydantic Models, SQLAlchemy, Repositories         │
├────────────────────────────────────────────────────────┤
│           External Layer (integrations/)                 │
│           CRM, PJe, EPROC, Notifications                 │
└────────────────────────────────────────────────────────┘
```

**Regra de ouro**: Dependências sempre apontam de fora para dentro. `channels/` depende de `core/`, mas `core/` NUNCA importa de `channels/`.

### 3.2 Interfaces e Dependency Injection

Cada integração externa deve ter uma interface abstrata:

```python
# src/channels/base.py
from abc import ABC, abstractmethod
from src.models.conversation import IncomingMessage, OutgoingMessage

class ChannelAdapter(ABC):
    """Interface base para todos os canais de mensagem."""

    @abstractmethod
    async def parse_webhook(self, raw_data: dict) -> IncomingMessage:
        """Converte payload do webhook em mensagem normalizada."""
        ...

    @abstractmethod
    async def send_message(self, message: OutgoingMessage) -> bool:
        """Envia mensagem pelo canal."""
        ...

    @abstractmethod
    async def send_document(self, chat_id: str, file_path: str, caption: str) -> bool:
        """Envia documento (PDF, DOCX) pelo canal."""
        ...
```

```python
# src/integrations/crm.py
from abc import ABC, abstractmethod
from src.models.lead import Lead

class CRMInterface(ABC):
    @abstractmethod
    async def create_lead(self, lead: Lead) -> str:
        """Cria lead no CRM. Retorna ID."""
        ...

    @abstractmethod
    async def update_lead(self, lead_id: str, data: dict) -> bool:
        ...

class PipedriveCRM(CRMInterface):
    """Implementação concreta para Pipedrive."""
    async def create_lead(self, lead: Lead) -> str:
        # implementação Pipedrive
        ...
```

### 3.3 Modelo de Conversa Normalizado

```python
# src/models/conversation.py
from pydantic import BaseModel
from enum import Enum
from datetime import datetime

class ChannelType(str, Enum):
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    INSTAGRAM = "instagram"

class MessageType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"

class IncomingMessage(BaseModel):
    channel: ChannelType
    channel_user_id: str          # ID do usuário no canal
    message_type: MessageType
    text: str | None = None       # Texto ou transcrição
    media_url: str | None = None  # URL do áudio/imagem
    timestamp: datetime
    raw_payload: dict             # Payload original do webhook

class ConversationState(BaseModel):
    session_id: str
    channel: ChannelType
    lead_id: str | None = None
    current_step: str             # Etapa atual do fluxo
    triage_answers: list[dict] = []
    area_juridica: str | None = None
    urgency: str | None = None
    score: int = 0
    lgpd_consent: bool = False
    is_existing_client: bool = False
    handoff_requested: bool = False
    history: list[dict] = []      # Histórico para o LLM
```

---

## 4. Configuração com Pydantic Settings

```python
# src/config/settings.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    app_name: str = "Agente Jurídico Breviliere"
    debug: bool = False
    log_level: str = "INFO"

    # LLM
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_model_light: str = "gpt-4o-mini"  # Para triagem leve

    # Embeddings / Vector Store
    embedding_model: str = "text-embedding-3-small"
    chroma_persist_dir: str = "./data/chroma"

    # Database
    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/juridico"
    redis_url: str = "redis://localhost:6379/0"

    # Channels
    whatsapp_verify_token: str = ""
    whatsapp_api_token: str = ""
    whatsapp_phone_number_id: str = ""
    telegram_bot_token: str = ""
    instagram_access_token: str = ""

    # Integrations
    crm_provider: str = "pipedrive"  # pipedrive | hubspot
    crm_api_key: str = ""
    slack_webhook_url: str = ""
    notification_email: str = ""

    # Whisper
    whisper_model: str = "whisper-1"

    # LGPD
    privacy_policy_url: str = ""
    terms_of_use_url: str = ""
    data_retention_days: int = 1825  # 5 anos

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

---

## 5. LangGraph — Estrutura do Agente

```python
# src/core/agent.py — Esqueleto conceitual
from langgraph.graph import StateGraph, END
from src.models.conversation import ConversationState

def build_agent_graph() -> StateGraph:
    """Constrói o grafo de estados do agente."""

    graph = StateGraph(ConversationState)

    # Nós (cada um é uma função async)
    graph.add_node("check_consent", check_lgpd_consent)
    graph.add_node("identify_client", identify_existing_client)
    graph.add_node("triage", run_triage_step)
    graph.add_node("classify_area", classify_legal_area)
    graph.add_node("qualify_lead", calculate_lead_score)
    graph.add_node("generate_briefing", generate_briefing)
    graph.add_node("rag_answer", answer_with_rag)
    graph.add_node("handoff", transfer_to_human)
    graph.add_node("process_query", query_judicial_process)
    graph.add_node("respond", send_response)

    # Edges condicionais
    graph.set_entry_point("check_consent")
    graph.add_conditional_edges("check_consent", route_after_consent)
    graph.add_conditional_edges("identify_client", route_after_identification)
    graph.add_edge("triage", "classify_area")
    graph.add_conditional_edges("classify_area", route_after_classification)
    graph.add_edge("qualify_lead", "generate_briefing")
    graph.add_edge("generate_briefing", "handoff")
    graph.add_edge("handoff", "respond")
    graph.add_edge("rag_answer", "respond")
    graph.add_edge("process_query", "respond")
    graph.add_edge("respond", END)

    return graph.compile()
```

---

## 6. RAG — Estratégia de Indexação

### Chunking por tipo de documento

| Tipo | Chunk Size | Overlap | Motivo |
|---|---|---|---|
| FAQ | 512 tokens | 50 | Respostas curtas e autocontidas |
| Jurisprudência | 1024 tokens | 128 | Textos longos com contexto legal |
| Legislação | 768 tokens | 100 | Artigos com referências cruzadas |
| Institucional | 256 tokens | 32 | Informações curtas e factuais |

### Metadados obrigatórios por chunk

```python
metadata = {
    "source": "faq/trabalhista.md",
    "area_juridica": "trabalhista",    # Para filtrar na busca
    "tipo": "faq",                      # faq | jurisprudencia | legislacao | institucional
    "data_atualizacao": "2026-02-28",
    "tags": ["rescisao", "verbas", "clt"]
}
```

### Script de indexação

```python
# scripts/seed_knowledge_base.py
"""
Uso: python scripts/seed_knowledge_base.py [--reset]

Indexa todos os documentos em knowledge_base/ no ChromaDB.
Use --reset para limpar a collection antes de reindexar.
"""
```

---

## 7. Docker Compose — Ambiente Local

```yaml
# docker/docker-compose.yml
services:
  app:
    build: .
    ports: ["8000:8000"]
    env_file: ../.env
    depends_on: [postgres, redis, chroma]
    volumes:
      - ../knowledge_base:/app/knowledge_base
      - ../data:/app/data

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: juridico
      POSTGRES_USER: juridico
      POSTGRES_PASSWORD: juridico_dev
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  chroma:
    image: chromadb/chroma:latest
    ports: ["8001:8000"]
    volumes: [chromadata:/chroma/chroma]

volumes:
  pgdata:
  chromadata:
```

---

## 8. Personalidade do Agente

```python
# src/core/personality.py

PERSONALITY = {
    "nome": "Assistente Jurídico Breviliere",
    "tom": "Profissional, acolhedor e empático",
    "linguagem": "Formal mas simplificada — sem juridiquês",
    "regras": [
        "Nunca fornecer aconselhamento jurídico direto",
        "Sempre esclarecer que é um assistente virtual",
        "Usar linguagem inclusiva e acessível",
        "Demonstrar empatia em situações sensíveis",
        "Manter sigilo absoluto sobre informações de outros clientes",
        "Sempre solicitar aceite LGPD antes de coletar dados",
    ],
}

SYSTEM_PROMPT = """
Você é o {nome}, assistente virtual do escritório Breviliere Advocacia.

## Personalidade
- Tom: {tom}
- Linguagem: {linguagem}

## Regras invioláveis
{regras}

## Contexto
Você está conversando via {canal} com um potencial cliente.
Sua função é acolher, entender a situação jurídica, e encaminhar
para o advogado mais indicado.

## Base de conhecimento
Use APENAS as informações da base de conhecimento fornecida.
Se não tiver informação suficiente, diga que precisa verificar
com a equipe jurídica. NUNCA invente informações jurídicas.
"""
```

---

## 9. Perguntas de Triagem

```python
# src/triage/questions.py

TRIAGE_QUESTIONS = {
    "geral": [
        {"id": "nome", "pergunta": "Qual seu nome completo?", "obrigatoria": True},
        {"id": "contato", "pergunta": "Qual seu telefone e e-mail para contato?", "obrigatoria": True},
        {"id": "cidade_estado", "pergunta": "Em qual cidade e estado você está?", "obrigatoria": True},
        {"id": "motivo", "pergunta": "Me conte brevemente o que está acontecendo. Qual o motivo do seu contato?", "obrigatoria": True},
        {"id": "urgencia", "pergunta": "Existe alguma urgência? (prazo vencendo, audiência marcada, etc.)", "obrigatoria": True},
        {"id": "outro_advogado", "pergunta": "Já consultou outro advogado sobre este assunto?", "obrigatoria": False},
        {"id": "acao_judicial", "pergunta": "Já existe alguma ação judicial em andamento?", "obrigatoria": False},
        {"id": "documentos", "pergunta": "Possui documentos relacionados ao caso? (contratos, notificações, etc.)", "obrigatoria": False},
    ],
    "trabalhista": [
        {"id": "vinculo", "pergunta": "Qual o tipo de vínculo? (CLT, PJ, temporário)", "obrigatoria": True},
        {"id": "tempo_empresa", "pergunta": "Há quanto tempo trabalha/trabalhou na empresa?", "obrigatoria": True},
        {"id": "verbas", "pergunta": "Recebeu todas as verbas rescisórias corretamente?", "obrigatoria": True},
        {"id": "ctps", "pergunta": "Sua CTPS está assinada? Possui contracheques?", "obrigatoria": False},
    ],
    "civil": [
        {"id": "tipo_civil", "pergunta": "Trata-se de: contrato, dívida, danos, consumidor ou outro?", "obrigatoria": True},
        {"id": "contraparte", "pergunta": "Quem é a outra parte envolvida? (pessoa física, empresa)", "obrigatoria": True},
        {"id": "valor", "pergunta": "Qual o valor aproximado envolvido?", "obrigatoria": False},
    ],
    "familia": [
        {"id": "tipo_familia", "pergunta": "Trata-se de: divórcio, pensão, guarda, inventário ou outro?", "obrigatoria": True},
        {"id": "filhos", "pergunta": "Há filhos menores envolvidos?", "obrigatoria": True},
        {"id": "acordo", "pergunta": "Existe possibilidade de acordo entre as partes?", "obrigatoria": False},
    ],
}
```

---

## 10. Ordem de Implementação (Sprint-by-Sprint)

### Sprint 1 — Fundação (Semana 1-2)
1. Criar estrutura de pastas completa
2. Configurar `pyproject.toml` com dependências
3. Implementar `config/settings.py` e `.env.example`
4. Configurar `docker-compose.yml` (PostgreSQL + Redis + ChromaDB)
5. Implementar `api/health.py` (GET /health)
6. Implementar `config/logging.py` com structlog
7. Setup de testes (pytest + conftest.py)
8. **Validação**: `docker compose up` + `curl /health` → 200 OK

### Sprint 2 — Core + RAG (Semana 3-4)
1. Implementar modelos Pydantic (`models/`)
2. Implementar `database/connection.py` + migrations Alembic
3. Implementar `rag/indexer.py` (chunking + metadados)
4. Implementar `rag/embeddings.py`
5. Implementar `rag/retriever.py` (busca com filtros)
6. Implementar `rag/chains.py` (RetrievalQA com guardrails)
7. Criar conteúdo inicial em `knowledge_base/` (FAQ de 3 áreas)
8. Implementar `scripts/seed_knowledge_base.py`
9. **Validação**: Indexar FAQ → fazer pergunta → receber resposta correta

### Sprint 3 — Conversação + Triagem (Semana 5-6)
1. Implementar `core/personality.py` e `core/prompts.py`
2. Implementar `core/conversation.py` (ConversationState)
3. Implementar `core/session.py` (Redis sessions)
4. Implementar `triage/questions.py` + `triage/classifier.py`
5. Implementar `triage/qualifier.py` (lead scoring)
6. Implementar `triage/flows.py` (fluxo adaptativo)
7. Implementar `core/agent.py` (LangGraph StateMachine)
8. **Validação**: Simular conversa completa via teste → briefing gerado

### Sprint 4 — WhatsApp + Handoff (Semana 7-8)
1. Implementar `channels/base.py` (ChannelAdapter ABC)
2. Implementar `channels/whatsapp.py`
3. Implementar `api/webhooks.py` (POST /webhook/whatsapp)
4. Implementar `audio/transcriber.py` (Whisper)
5. Implementar `handoff/manager.py`
6. Implementar `integrations/notifications.py` (Slack/e-mail)
7. Implementar `documents/generator.py` (briefing PDF)
8. **Validação**: Mensagem WhatsApp → triagem → briefing → notificação

### Sprint 5 — CRM + Docs + Canais (Semana 9-10)
1. Implementar `integrations/crm.py` (Pipedrive/HubSpot)
2. Implementar `documents/generator.py` (proposta, contrato)
3. Implementar `channels/telegram.py`
4. Implementar `channels/instagram.py`
5. Implementar `api/admin.py` (painel básico)
6. **Validação**: Lead → CRM + documentos gerados + multi-canal

### Sprint 6 — Pós-venda + Polish (Semana 11-12)
1. Implementar `integrations/pje.py` e `integrations/eproc.py`
2. Implementar fluxo de consulta processual no agent.py
3. Testes E2E completos
4. Hardening de segurança (rate limiting, LGPD audit)
5. Documentação final
6. **Validação**: Fluxo completo end-to-end em todos os canais

---

## 11. Variáveis de Ambiente (.env.example)

```env
# === App ===
APP_NAME="Agente Jurídico Breviliere"
DEBUG=false
LOG_LEVEL=INFO

# === LLM ===
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
OPENAI_MODEL_LIGHT=gpt-4o-mini

# === Embeddings / Vector Store ===
EMBEDDING_MODEL=text-embedding-3-small
CHROMA_PERSIST_DIR=./data/chroma

# === Database ===
DATABASE_URL=postgresql+asyncpg://juridico:juridico_dev@localhost:5432/juridico
REDIS_URL=redis://localhost:6379/0

# === WhatsApp ===
WHATSAPP_VERIFY_TOKEN=seu_token_de_verificacao
WHATSAPP_API_TOKEN=seu_token_api
WHATSAPP_PHONE_NUMBER_ID=seu_phone_id

# === Telegram ===
TELEGRAM_BOT_TOKEN=seu_bot_token

# === Instagram ===
INSTAGRAM_ACCESS_TOKEN=seu_access_token

# === CRM ===
CRM_PROVIDER=pipedrive
CRM_API_KEY=seu_crm_key

# === Notifications ===
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
NOTIFICATION_EMAIL=equipe@breviliere.com.br

# === LGPD ===
PRIVACY_POLICY_URL=https://breviliere.com.br/privacidade
TERMS_OF_USE_URL=https://breviliere.com.br/termos
DATA_RETENTION_DAYS=1825
```

---

## 12. Regras de Qualidade de Código

1. **Type hints obrigatórios** em todas as funções públicas
2. **Docstrings** em todas as classes e funções públicas
3. **Async/await** para toda I/O (HTTP, DB, Redis, APIs)
4. **Pydantic** para validação de todos os dados de entrada
5. **Testes** mínimo 80% de cobertura no core/
6. **Sem segredos** no código — tudo via `.env`
7. **Logs estruturados** com contexto `session_id` e `channel`
8. **Error handling** com fallback gracioso (nunca expor stack trace ao usuário)
9. **Imports absolutos** a partir de `src.` (ex: `from src.core.agent import ...`)
10. **Separação estrita** entre camadas — channels nunca acessa database diretamente
