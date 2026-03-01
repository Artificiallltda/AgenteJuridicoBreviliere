# Guia de Instalação — Agente Jurídico (Breviliere)

Este documento descreve os passos necessários para configurar o ambiente de desenvolvimento local.

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado:
- [Python 3.12+](https://www.python.org/)
- [uv](https://github.com/astral-sh/uv) (Gerenciador de pacotes ultra-rápido)
- [Docker & Docker Compose](https://www.docker.com/)
- [Git](https://git-scm.com/)

---

## 🛠️ Passo a Passo da Instalação

### 1. Clonar o Repositório
```bash
git clone <url-do-repositorio>
cd agente-juridico-breviliere
```

### 2. Configurar o Ambiente Python com `uv`
O `uv` gerencia o ambiente virtual e as dependências de forma otimizada.
```bash
# Cria o ambiente virtual e instala dependências
uv venv
uv sync
```

### 3. Variáveis de Ambiente
Copie o arquivo de exemplo e preencha com suas credenciais (OpenAI, Meta, Pipedrive).
```bash
cp .env.example .env
```
*Edite o `.env` com sua `OPENAI_API_KEY` e tokens de canal.*

### 4. Subir a Infraestrutura (Docker)
Inicie o banco de dados PostgreSQL, Redis e ChromaDB.
```bash
docker compose -f docker/docker-compose.yml up -d
```

### 5. Inicializar o Banco de Dados (Alembic)
Gere as tabelas no PostgreSQL.
```bash
uv run alembic upgrade head
```

### 6. Popular a Base de Conhecimento (RAG)
Indexe os documentos jurídicos iniciais no ChromaDB.
```bash
uv run python scripts/seed_knowledge_base.py --reset
```

### 7. Iniciar o Servidor de Desenvolvimento
```bash
uv run uvicorn src.main:app --reload
```
A API estará disponível em `http://localhost:8000/docs`.

---

## 🧪 Validando a Instalação
Para garantir que tudo está funcionando corretamente, execute os testes:
```bash
uv run pytest tests/test_seed.py
uv run pytest tests/test_e2e_agent.py
```
