# Code Review — Sprints 1-2 (Agente Jurídico Breviliere)

**Data:** 28/02/2026 | **Revisor:** Antigravity | **Arquivos revisados:** 15 Python + Docker + requirements

---

## Resumo Executivo

| Severidade | Contagem | Impacto |
|---|---|---|
| 🔴 Crítico | 2 | Quebra em produção |
| 🟠 Alto | 4 | Bugs ou problemas de segurança |
| 🟡 Médio | 4 | Manutenibilidade ou performance |
| 🔵 Baixo | 2 | Boas práticas |

---

## 🔴 Críticos

### C1. `main.py` — API depreciada `on_event`

> [!CAUTION]
> `@app.on_event("startup")` foi **depreciado no FastAPI 0.110+**. Vai gerar warnings e será removido em versões futuras.

```diff
 # src/main.py
-@app.on_event("startup")
-async def startup_event():
-    logger.info("iniciando_aplicacao", app_name=settings.app_name, debug=settings.debug)
+from contextlib import asynccontextmanager
+
+@asynccontextmanager
+async def lifespan(app: FastAPI):
+    logger.info("iniciando_aplicacao", app_name=settings.app_name, debug=settings.debug)
+    yield
+    logger.info("encerrando_aplicacao")
+
+app = FastAPI(
+    title=settings.app_name,
+    debug=settings.debug,
+    lifespan=lifespan,
+)
```

---

### C2. `agent.py` — Código executado no escopo de módulo

> [!CAUTION]
> Linha 189: `logger.info("grafo_agente_construido_com_sucesso")` executa **durante o import**, não dentro de uma função. Isso causa log falso e pode crashar se o logger não estiver pronto.

```diff
 # src/core/agent.py — Linha 189
-logger.info("grafo_agente_construido_com_sucesso")
+# Removido: log de módulo fora de função
```

---

## 🟠 Altos

### A1. `settings.py` — Falta `model_config` do Pydantic v2

A classe interna `Config` é o estilo Pydantic v1. Com `pydantic-settings>=2.2`:

```diff
 class Settings(BaseSettings):
     # ...
-    class Config:
-        env_file = ".env"
-        env_file_encoding = "utf-8"
+    model_config = {
+        "env_file": ".env",
+        "env_file_encoding": "utf-8",
+    }
```

> [!IMPORTANT]
> O `class Config` ainda funciona, mas gera `DeprecationWarning`. Melhor migrar agora.

---

### A2. `embeddings.py` — Cliente OpenAI instanciado no escopo de módulo

```python
# Linha 442 — executa no import, antes do .env estar carregado
client = AsyncOpenAI(api_key=settings.openai_api_key)
```

**Problema:** Se `OPENAI_API_KEY` não estiver no `.env` no momento do import, o client é criado com string vazia. Deveria ser lazy:

```diff
-client = AsyncOpenAI(api_key=settings.openai_api_key)
+_client = None
+
+def _get_client() -> AsyncOpenAI:
+    global _client
+    if _client is None:
+        _client = AsyncOpenAI(api_key=settings.openai_api_key)
+    return _client
 
 async def get_embeddings(texts: List[str]) -> List[List[float]]:
-    response = await client.embeddings.create(...)
+    response = await _get_client().embeddings.create(...)
```

**Mesmo problema em:** `triage/classifier.py` (linha 514).

---

### A3. `indexer.py` — Query não usa embeddings

```python
# Linha 496-503
def query(self, query_text: str, ...):
    return self.collection.query(
        query_texts=[query_text],  # ← ChromaDB gera embedding internamente
        ...
    )
```

**Problema de consistência:** O `index_documents` gera embeddings manualmente via OpenAI, mas o `query` usa o embedding function *padrão* do ChromaDB (que é diferente). Isso causa **mismatch de vetores** e respostas ruins.

```diff
-    def query(self, query_text: str, n_results: int = 3, filter: Dict = None):
+    async def query(self, query_text: str, n_results: int = 3, filter: Dict = None):
         """Busca os documentos mais relevantes."""
+        query_embedding = await get_embeddings([query_text])
         return self.collection.query(
-            query_texts=[query_text],
+            query_embeddings=query_embedding,
             n_results=n_results,
             where=filter
         )
```

---

### A4. Dockerfile **não existe**

O `docker-compose.yml` referencia `build: .` mas não existe um `Dockerfile` no projeto. O `docker compose up` vai falhar.

---

## 🟡 Médios

### M1. `connection.py` — `get_db` fecha sessão duas vezes

```python
async def get_db():
    async with AsyncSessionLocal() as session:  # ← context manager já chama close()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()  # ← Redundante! Já é fechada pelo 'async with'
```

```diff
 async def get_db():
     async with AsyncSessionLocal() as session:
         try:
             yield session
             await session.commit()
         except Exception as e:
             await session.rollback()
             logger.error("erro_sessao_banco", error=str(e))
             raise
-        finally:
-            await session.close()
```

---

### M2. `models/conversation.py` — `datetime.utcnow` depreciado

```python
timestamp: datetime = Field(default_factory=datetime.utcnow)  # Depreciado Python 3.12+
```

```diff
-from datetime import datetime
+from datetime import datetime, timezone
 
-    timestamp: datetime = Field(default_factory=datetime.utcnow)
+    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

**Mesmo problema em:** `models/lead.py`, `models/document.py`, `models/process.py` (todos usam `default=datetime.utcnow`).

Para SQLAlchemy, use:

```diff
-from datetime import datetime
+from datetime import datetime, timezone
 
-    created_at = Column(DateTime, default=datetime.utcnow)
+    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
```

---

### M3. `docker-compose.yml` — `env_file` caminho relativo incorreto

```yaml
app:
    build: .        # ← Procura Dockerfile no diretório docker/
    env_file: .env  # ← Procura .env em docker/, mas está na raiz
```

```diff
 app:
-    build: .
-    env_file: .env
+    build:
+      context: ..
+      dockerfile: docker/Dockerfile
+    env_file: ../.env
```

---

### M4. `requirements.txt` — Versões sem pin superior

```
fastapi>=0.110.0    # Pode instalar 1.0 breaking-change
langgraph>=0.2.0    # API instável, pode quebrar
```

Melhor usar range: `fastapi>=0.110.0,<1.0.0` ou migrar pra `pyproject.toml` com `uv.lock`.

---

## 🔵 Baixos

### B1. `models/` — Falta separação SQLAlchemy vs Pydantic

Os arquivos `lead.py`, `document.py`, `process.py` misturam modelo SQLAlchemy (ORM) e Pydantic (Schema) no mesmo arquivo. Funcionam, mas com o crescimento do projeto recomenda-se:

```
models/
├── schemas/           # Pydantic (API)
│   ├── lead.py
│   └── process.py
└── orm/               # SQLAlchemy (DB)
    ├── lead.py
    └── process.py
```

Não é urgente — refatorar quando houver mais de 10 modelos.

---

### B2. `questions.py` — Falta `criminal` e `previdenciário`

O PRD lista 5 áreas jurídicas, mas o banco de perguntas só tem 4 (falta `criminal` e `previdenciario`).

---

## Ações Recomendadas (Prioridade)

| # | Ação | Impacto | Esforço |
|---|---|---|---|
| 1 | Criar o `Dockerfile` | 🔴 Blocker p/ Docker | 5 min |
| 2 | Corrigir mismatch de embeddings no RAG query | 🔴 Respostas erradas | 5 min |
| 3 | Substituir `on_event` por `lifespan` | 🟠 Deprecation | 3 min |
| 4 | Lazy-init dos clientes OpenAI | 🟠 Crash no import | 5 min |
| 5 | Remover log no escopo do módulo (`agent.py`) | 🟠 Crash no import | 1 min |
| 6 | Migrar `class Config` → `model_config` | 🟡 Deprecation | 2 min |
| 7 | Corrigir `datetime.utcnow` → `datetime.now(UTC)` | 🟡 Deprecation | 3 min |
| 8 | Corrigir `docker-compose.yml` paths | 🟡 Blocker p/ Docker | 2 min |
| 9 | Remover `session.close()` redundante | 🟡 Clareza | 1 min |
