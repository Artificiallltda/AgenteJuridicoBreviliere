# Agente Jurídico Breviliere

**Versão:** 2.0 | **Atualizado:** 29/03/2026

---

## 📋 Visão Geral

O **Agente Jurídico Breviliere** é um assistente virtual de IA para escritórios de advocacia. Ele automatiza o **atendimento inicial** de clientes, realizando triagem jurídica, qualificação de leads e encaminhamento para advogados humanos — tudo via WhatsApp, Telegram e Instagram.

### 🎯 O Que Faz

- ✅ Atendimento multicanal (WhatsApp, Telegram, Instagram)
- ✅ Triagem jurídica adaptativa (6 áreas)
- ✅ Classificação automática via IA (GPT-4o)
- ✅ Score de lead (0-100)
- ✅ Transcrição de áudio (Whisper)
- ✅ Geração de documentos (DOCX)
- ✅ Integração CRM (Pipedrive)
- ✅ Handoff para advogado (Slack)
- ✅ Base de conhecimento RAG (ChromaDB)
- ✅ Dashboard de métricas

---

## 🤖 Squad de Agentes

O sistema é composto por **11 agentes especializados**:

### Agentes de Linha de Frente

| Agente | Função | Ativação |
|---|---|---|
| **@minato** | Atendimento e triagem de clientes | `@minato`, `*minato` |
| **@copywriter** | Tom de voz e copywriting | `@copy`, `*copy` |

### Agentes de Bastidores

| Agente | Função | Ativação |
|---|---|---|
| **@kakashi** | Estratégia de bastidores | `@kakashi`, `*kakashi` |
| **@tsunade** | Inteligência de mercado | `@tsunade`, `*tsunade` |
| **@kabuto** | Análise de prazos/e-mails | `@kabuto`, `*kabuto` |

### Agentes de Conteúdo

| Agente | Função | Ativação |
|---|---|---|
| **@ero-sennin** | Conteúdo para redes sociais | `@ero`, `*ero` |
| **@sai** | Geração de imagens | `@sai`, `*sai` |

### Agentes Técnicos

| Agente | Função | Ativação |
|---|---|---|
| **@sakura** | Peças processuais | `@sakura`, `*sakura` |
| **@dev** | Desenvolvimento Python | `@dev`, `*dev` |
| **@qa** | Qualidade e testes | `@qa`, `*qa` |

### Agentes de Gestão

| Agente | Função | Ativação |
|---|---|---|
| **@pm** | Product management | `@pm`, `*pm` |

📖 **Guia Completo:** Veja [`docs/AGENTS_GUIDE.md`](docs/AGENTS_GUIDE.md) para detalhes de cada agente.

---

## 🌊 Fluxo de Atendimento

```
Cliente envia mensagem (texto ou áudio)
        │
        ▼
┌─────────────────────────┐
│  WhatsApp / Telegram /  │
│      Instagram          │
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐     ┌──────────────┐
│  Webhook FastAPI        │────▶│  Whisper API  │ (se áudio)
│  Recebe e roteia        │     │  Áudio→Texto  │
└─────────┬───────────────┘     └──────────────┘
          │
          ▼
┌─────────────────────────┐
│  1. Consentimento LGPD  │  "Você aceita nossos termos?"
│     (obrigatório)       │
└─────────┬───────────────┘
          │ "Sim"
          ▼
┌─────────────────────────┐
│  2. Triagem Adaptativa  │  Perguntas inteligentes
│     6 áreas jurídicas   │  (pula irrelevantes)
│     Pesos + Condicionais│
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│  3. Classificação IA    │  LLM classifica a área
│     (OpenAI GPT-4o)     │  jurídica automaticamente
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│  4. Score de Lead       │  0-100 baseado em pesos,
│     (qualificação)      │  urgência e documentos
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│  5. Briefing + CRM      │  Gera DOCX + cria lead
│     Pipedrive           │  no Pipedrive (Person +
│                         │  Deal + Nota)
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────┐
│  6. Handoff Humano      │  Notificação via Slack
│     via Slack           │  com briefing completo
└─────────────────────────┘
```

---

## 🚀 Instalação Rápida

### Requisitos

- Docker e Docker Compose
- Conta OpenAI (API key)
- Conta Meta Business (WhatsApp/Instagram)
- Bot Telegram (@BotFather)
- Conta Pipedrive (CRM)
- Slack Workspace (webhook)

### Passos

```bash
# 1. Clonar repositório
git clone <repo-url>
cd agente-juridico-breviliere

# 2. Copiar configurações
cp .env.example .env
# Editar .env com suas chaves de API

# 3. Subir tudo
docker compose up --build

# 4. Popular base de conhecimento
docker exec -it app python -m scripts.seed_knowledge_base

# 5. Configurar webhooks
# WhatsApp: Meta Dashboard → Webhook URL → https://seu-dominio/webhooks/whatsapp
# Telegram: curl -X POST "https://api.telegram.org/bot{TOKEN}/setWebhook?url=https://seu-dominio/webhooks/telegram"
# Instagram: Meta Dashboard → Webhook URL → https://seu-dominio/webhooks/instagram
```

### Endpoints Disponíveis

| URL | Descrição |
|---|---|
| `GET /health` | Health check |
| `POST /webhooks/whatsapp` | Webhook WhatsApp |
| `POST /webhooks/telegram` | Webhook Telegram |
| `POST /webhooks/instagram` | Webhook Instagram |
| `GET /admin/kb/*` | Admin da KB |
| `GET /admin/dashboard/*` | Dashboard de métricas |

---

## 📚 Estrutura do Projeto

```
agente-juridico-breviliere/
├── src/
│   ├── api/           → Endpoints (webhooks, admin, dashboard)
│   ├── audio/         → Transcrição de áudio (Whisper)
│   ├── channels/      → Adaptadores (WhatsApp, Telegram, Instagram)
│   ├── config/        → Configurações e logging
│   ├── core/          → Motor de conversa, LLM, prompts, agent-router
│   ├── database/      → Conexão PostgreSQL
│   ├── documents/     → Geração de documentos DOCX
│   ├── handoff/       → Transferência para humano + CRM
│   ├── integrations/  → CRM, Pipedrive, notificações
│   ├── models/        → Modelos Pydantic
│   ├── rag/           → Pipeline RAG (indexação + consulta)
│   └── triage/        → Triagem adaptativa
├── squads/
│   └── juridico-squad/
│       └── agents/    → Agentes especializados (11 agentes)
├── knowledge_base/
│   ├── faq/           → Perguntas frequentes
│   ├── institucional/ → Informações do escritório
│   ├── jurisprudencia/→ Súmulas e jurisprudência
│   └── templates_texto/→ Templates de mensagens
├── scripts/           → Scripts de seed e utilitários
├── tests/             → Testes unitários e de integração
├── docs/              → Documentação completa
├── docker/            → Configurações Docker
├── docker-compose.yml → Orquestração de serviços
└── requirements.txt   → Dependências Python
```

---

## 🧪 Testes

```bash
# Rodar todos os testes
docker exec -it app pytest

# Rodar com cobertura
docker exec -it app pytest --cov=src --cov-report=html

# Rodar testes específicos
docker exec -it app pytest tests/unit/test_conversation.py -v
```

---

## 📊 Dashboard de Métricas

Acesse `GET /admin/dashboard/metrics` para:

| Métrica | Descrição |
|---|---|
| Total de conversas | Número total de conversas iniciadas |
| Conversas ativas | Conversas em andamento |
| Conversas fechadas | Conversas finalizadas |
| Por canal | WhatsApp vs Telegram vs Instagram |
| Por área jurídica | Distribuição por área do direito |
| Score médio | Qualidade média dos leads |

---

## 🔒 Segurança e Compliance

| Item | Implementação |
|---|---|
| **LGPD** | Consentimento explícito antes de coleta |
| **Webhook Auth** | Validação X-Hub-Signature-256 (Meta) |
| **API Keys** | Bearer token em headers |
| **Dados sensíveis** | Variáveis de ambiente (.env) |
| **IA transparente** | Agente se identifica como IA |

---

## 📖 Documentação Completa

| Documento | Descrição |
|---|---|
| [`docs/AGENTS_GUIDE.md`](docs/AGENTS_GUIDE.md) | Guia de todos os agentes |
| [`docs/INSTALLATION.md`](docs/INSTALLATION.md) | Instalação detalhada |
| [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) | Guia de deploy |
| [`docs/OPERATIONS.md`](docs/OPERATIONS.md) | Operações diárias |
| [`docs/PRD.md`](docs/prd/PRD.md) | Product Requirements Document |

---

## 🛠️ Stack Tecnológico

| Componente | Tecnologia |
|---|---|
| **Runtime** | Python 3.12 |
| **Framework** | FastAPI + Uvicorn |
| **IA/LLM** | OpenAI GPT-4o / GPT-4o-mini |
| **Transcrição** | OpenAI Whisper |
| **Embeddings** | OpenAI text-embedding-3-small |
| **Banco Vetorial** | ChromaDB |
| **Banco de Dados** | PostgreSQL 16 |
| **Cache** | Redis 7 |
| **CRM** | Pipedrive |
| **Notificações** | Slack Webhooks |
| **Documentos** | python-docxtpl |
| **Deploy** | Docker + Docker Compose |

---

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique [`docs/OPERATIONS.md`](docs/OPERATIONS.md) para troubleshooting
2. Consulte o dashboard de métricas para diagnóstico
3. Abra uma issue no repositório

---

## 📄 Licença

Copyright © 2026 Breviliere Advocacia. Todos os direitos reservados.

---

## 🎯 Roadmap

| Feature | Status | Descrição |
|---|---|---|
| Consulta PJe/EPROC | 🔴 Mock | Consulta processual real via MNI |
| Frontend admin | 🔴 | Interface web para painel admin |
| Notificações proativas | ⏳ | Follow-up automático com clientes |
| Multi-idioma | 🔴 | Suporte a espanhol e inglês |
| Analytics avançados | 🔴 | Gráficos e relatórios exportáveis |
