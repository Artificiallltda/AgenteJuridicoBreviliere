# Agente Jurídico Breviliere — Documentação Completa

**Versão:** 1.0 | **Data:** 01/03/2026

---

## 1. O Que É

O **Agente Jurídico Breviliere** é um assistente virtual de IA para escritórios de advocacia. Ele automatiza o **atendimento inicial** de clientes, realizando triagem jurídica, qualificação de leads e encaminhamento para advogados humanos — tudo via WhatsApp, Telegram e Instagram.

### Resumo Visual do Fluxo

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

## 2. Canais de Atendimento

| Canal | O Que Faz | Como Configura |
|---|---|---|
| **WhatsApp** | Recebe texto e áudio, responde automaticamente | Meta Business API + webhook |
| **Telegram** | Recebe texto e áudio, responde automaticamente | BotFather + webhook |
| **Instagram** | Recebe texto e áudio, responde automaticamente | Meta Developer Portal + webhook |

Todos os canais compartilham a **mesma inteligência** — o mesmo fluxo de conversa, triagem e handoff.

---

## 3. Fluxo de Conversa Detalhado

### 3.1 Consentimento LGPD

Antes de qualquer coleta de dados, o agente pergunta:

> *"Para sua segurança e em conformidade com a LGPD, precisamos do seu consentimento para processar seus dados pessoais. Você aceita?"*

O cliente deve responder "Sim" ou "Aceito" para prosseguir. **Sem consentimento, o agente não coleta dados.**

### 3.2 Triagem Adaptativa

O sistema faz perguntas inteligentes baseadas em **6 áreas jurídicas**:

| Área | Perguntas Específicas |
|---|---|
| **Geral** | Nome, cidade, motivo, urgência, documentos |
| **Trabalhista** | Tipo de vínculo, tempo de empresa, verbas, FGTS |
| **Civil** | Tipo (contrato/dívida/consumidor), contraparte, valor |
| **Família** | Tipo (divórcio/pensão/guarda), filhos menores, consenso |
| **Criminal** | Liberdade/preso, processo existente, fase |
| **Previdenciário** | Benefício buscado, requerimento INSS, negativa |

**Adaptativa** significa que:
- Perguntas **irrelevantes são puladas** (ex: "Quais documentos?" só aparece se disse que tem documentos)
- O sistema mostra o **progresso**: "Progresso: 3/10 perguntas"
- Cada pergunta tem um **peso** (1-10) usado no cálculo do score

### 3.3 Classificação Automática via IA

Após a 3ª resposta, o sistema usa **GPT-4o** para classificar automaticamente a área jurídica do caso, ajustando as perguntas restantes para a área identificada.

### 3.4 Score de Lead (0-100)

O score é calculado por:
- **Soma dos pesos** das perguntas respondidas
- **Bônus +15** se declarou urgência
- **Bônus +10** se possui documentos
- Normalizado para escala 0-100

| Score | Classificação | Ação |
|---|---|---|
| 0-40 | Frio | Registra no CRM |
| 41-70 | Morno | Registra + notifica equipe |
| 71-100 | Quente | Registra + gera proposta automática |

### 3.5 Transcrição de Áudio

Se o cliente enviar um **áudio** em vez de texto:
1. O sistema **baixa o arquivo** de áudio (WhatsApp/Telegram/Instagram)
2. **Transcreve** usando OpenAI Whisper
3. **Processa** o texto transcrito como se fosse uma mensagem de texto

### 3.6 Geração de Documentos

O sistema gera automaticamente **3 tipos de documentos DOCX**:

| Documento | Quando | Para Quem |
|---|---|---|
| **Briefing** | Fim da triagem | Equipe interna (advogados) |
| **Proposta de Honorários** | Score ≥ 80 | Cliente (enviado pelo advogado) |
| **Contrato** | Após aprovação | Cliente (assinatura) |

### 3.7 Integração CRM (Pipedrive)

Ao final do atendimento, o sistema cria automaticamente no Pipedrive:
1. **Person** (contato do cliente com nome, telefone, área jurídica)
2. **Deal** (negócio vinculado à pessoa)
3. **Note** (briefing completo da triagem anexado ao negócio)

### 3.8 Handoff para Advogado

A notificação no Slack inclui:
- Nome do cliente e canal de origem
- Área jurídica e score de qualificação
- ID do CRM (link direto para o Pipedrive)
- Briefing completo (todas as perguntas e respostas)

---

## 4. Base de Conhecimento (RAG)

O sistema possui uma **base de conhecimento vetorial** (ChromaDB) que permite:
- Responder perguntas baseadas em **documentos do escritório**
- Busca **semântica** (entende significado, não apenas palavras-chave)

### Conteúdo Atual

| Categoria | Descrição |
|---|---|
| **FAQ** | Perguntas frequentes sobre áreas jurídicas |
| **Institucional** | Informações sobre o escritório |
| **Modelos** | Templates de documentos jurídicos |
| **Situações** | Guias para situações jurídicas comuns |

### API Admin da KB

Os administradores podem gerenciar a KB via API REST:

| Endpoint | Ação |
|---|---|
| `GET /admin/kb/documents` | Listar documentos |
| `POST /admin/kb/documents` | Adicionar novo documento |
| `PUT /admin/kb/documents/{id}` | Atualizar documento |
| `DELETE /admin/kb/documents/{id}` | Remover documento |
| `POST /admin/kb/search` | Busca semântica |
| `GET /admin/kb/stats` | Estatísticas da KB |

---

## 5. Dashboard de Métricas

API para monitorar o desempenho do agente em tempo real:

| Endpoint | O Que Mostra |
|---|---|
| `GET /admin/dashboard/metrics` | Total de conversas, ativas, fechadas, por canal, por área, score médio |
| `GET /admin/dashboard/conversations` | Lista de todas as conversas (filtros por canal, step, score) |
| `GET /admin/dashboard/conversations/{id}` | Detalhe completo de uma conversa |
| `GET /admin/dashboard/conversations/{id}/history` | Histórico de mensagens |

---

## 6. Arquitetura Técnica

### Stack

| Componente | Tecnologia |
|---|---|
| **Backend** | Python 3.12 + FastAPI |
| **IA/LLM** | OpenAI GPT-4o / GPT-4o-mini |
| **Transcrição** | OpenAI Whisper |
| **Embeddings** | OpenAI text-embedding-3-small |
| **Banco Vetorial** | ChromaDB |
| **Banco de Dados** | PostgreSQL 16 |
| **Cache** | Redis 7 |
| **CRM** | Pipedrive |
| **Notificações** | Slack Webhooks |
| **Documentos** | python-docxtpl (DOCX) |
| **Deploy** | Docker + Docker Compose |

### Estrutura de Módulos

```
agente-juridico-breviliere/
├── src/
│   ├── api/           → Endpoints (webhooks, admin KB, dashboard)
│   ├── audio/         → Transcrição de áudio (Whisper)
│   ├── channels/      → Adaptadores (WhatsApp, Telegram, Instagram)
│   ├── config/        → Configurações e logging
│   ├── core/          → Motor de conversa, LLM, prompts
│   ├── database/      → Conexão PostgreSQL
│   ├── documents/     → Geração de documentos DOCX
│   ├── handoff/       → Transferência para humano + CRM
│   ├── integrations/  → CRM, Pipedrive, PJe, EPROC, notificações
│   ├── models/        → Modelos Pydantic
│   ├── rag/           → Pipeline RAG (indexação + consulta)
│   └── triage/        → Triagem adaptativa (perguntas + classificação + score)
├── knowledge_base/    → Documentos da base de conhecimento
├── scripts/           → Scripts de seed e criação de templates
├── tests/             → Testes unitários (14 arquivos)
├── Dockerfile         → Imagem Docker
└── docker-compose.yml → Orquestração (app + redis + postgres)
```

### Diagrama de Dependências

```
                    ┌──────────┐
                    │  main.py │
                    │ (FastAPI)│
                    └────┬─────┘
           ┌─────────────┼──────────────┐
           ▼             ▼              ▼
     ┌──────────┐  ┌──────────┐  ┌──────────────┐
     │ webhooks │  │  admin   │  │  dashboard   │
     │ (API)    │  │  (KB)    │  │  (métricas)  │
     └────┬─────┘  └────┬─────┘  └──────────────┘
          │              │
          ▼              ▼
     ┌──────────┐  ┌──────────┐
     │ channels │  │   RAG    │
     │ (3 adapt)│  │ (ChromaDB│
     └────┬─────┘  └──────────┘
          │
          ▼
     ┌──────────────────────────────┐
     │      conversation.py        │
     │  (motor central do agente)  │
     └──────┬───────┬───────┬──────┘
            │       │       │
            ▼       ▼       ▼
      ┌────────┐ ┌────┐ ┌────────┐
      │ triage │ │ LLM│ │handoff │
      │(adaptat│ │    │ │+CRM   │
      └────────┘ └────┘ └────────┘
```

---

## 7. Segurança e Compliance

| Item | Implementação |
|---|---|
| **LGPD** | Consentimento explícito antes de qualquer coleta |
| **Webhook Auth** | Validação de assinatura X-Hub-Signature-256 (Meta) |
| **API Keys** | Bearer token em headers (nunca em URL) |
| **Dados sensíveis** | Configurações via variáveis de ambiente (.env) |
| **IA transparente** | O agente se identifica como IA e nunca dá aconselhamento jurídico |

---

## 8. Como Subir o Sistema

### Requisitos
- Docker e Docker Compose instalados
- Conta OpenAI (API key)
- Conta Meta Business (WhatsApp/Instagram)
- Bot Telegram (@BotFather)
- Conta Pipedrive (CRM)
- Slack Workspace (webhook)

### Passos

```bash
# 1. Copiar configurações
cp .env.example .env
# Editar .env com suas chaves de API

# 2. Subir tudo
docker compose up --build

# 3. Popular base de conhecimento
docker exec -it app python -m scripts.seed_knowledge_base

# 4. Configurar webhooks
# WhatsApp: Meta Dashboard → Webhook URL → https://seu-dominio/webhooks/whatsapp
# Telegram: curl -X POST "https://api.telegram.org/bot{TOKEN}/setWebhook?url=https://seu-dominio/webhooks/telegram"
# Instagram: Meta Dashboard → Webhook URL → https://seu-dominio/webhooks/instagram
```

### Endpoints Disponíveis

| URL | Descrição |
|---|---|
| `GET /health` | Health check da aplicação |
| `POST /webhooks/whatsapp` | Receber mensagens WhatsApp |
| `POST /webhooks/telegram` | Receber mensagens Telegram |
| `POST /webhooks/instagram` | Receber mensagens Instagram |
| `GET /admin/kb/*` | Painel admin da KB |
| `GET /admin/dashboard/*` | Dashboard de métricas |

---

## 9. Roadmap Futuro

| Feature | Status | Descrição |
|---|---|---|
| Consulta PJe/EPROC | 🔴 Mock | Consulta processual real via MNI |
| Frontend admin | 🔴 | Interface web para o painel admin |
| Notificações proativas | ⏳ Sprint 17 | Follow-up automático com clientes |
| Multi-idioma | 🔴 | Suporte a espanhol e inglês |
| Analytics avançados | 🔴 | Gráficos e relatórios exportáveis |
