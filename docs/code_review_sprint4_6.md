# Code Review — Sprints 4-6 (Agente Jurídico Breviliere)

**Data:** 28/02/2026 | **Revisor:** Antigravity | **Arquivos revisados:** 19

---

## Resumo Executivo

| Severidade | Contagem | Impacto |
|---|---|---|
| 🔴 Crítico | 3 | Crash ou falha de segurança |
| 🟠 Alto | 4 | Bugs ou comportamento incorreto |
| 🟡 Médio | 5 | Manutenibilidade ou funcionalidade incompleta |
| 🔵 Baixo | 2 | Boas práticas |

---

## 🔴 Críticos

### C1. `webhooks.py` — Payload do WhatsApp sem validação de assinatura

> [!CAUTION]
> O webhook POST do WhatsApp não valida a assinatura `X-Hub-Signature-256` da Meta. Qualquer pessoa pode enviar payloads falsos ao endpoint.

```diff
 # src/api/webhooks.py
+import hmac
+import hashlib
+
 @router.post("/whatsapp")
 async def receive_whatsapp(request: Request):
     data = await request.json()
+    # Validar assinatura da Meta
+    signature = request.headers.get("X-Hub-Signature-256", "")
+    body = await request.body()
+    expected = "sha256=" + hmac.new(
+        settings.whatsapp_app_secret.encode(),
+        body, hashlib.sha256
+    ).hexdigest()
+    if not hmac.compare_digest(signature, expected):
+        raise HTTPException(status_code=403, detail="Invalid signature")
```

> Requer adicionar `whatsapp_app_secret: str = ""` ao `settings.py`.

---

### C2. `eproc.py` e `pje.py` — Strings com escapes quebrados

Os arquivos têm `\"` (aspas escapadas) dentro das docstrings e strings, o que causa `SyntaxError`:

```python
# Linha 306 em eproc.py
\"\"\"Consulta processual simulada no EPROC (mock).\"\"\"  # ❌ SyntaxError
```

```diff
-    \"\"\"Consulta processual simulada no EPROC (mock).\"\"\"
+    """Consulta processual simulada no EPROC (mock)."""
```

**Mesmo problema em:** `pje.py` (linhas 352-357). Precisa reescrever esses 2 arquivos sem escapes.

---

### C3. `test_seed.py` — Importa a versão simplificada do seed

```python
from scripts.seed_knowledge_base import seed  # ❌ Importa a função "seed" que não existe na versão completa
```

O teste foi escrito para a versão simplificada do agente. Na versão completa, a função é `seed_knowledge_base`, não `seed`. Precisa atualizar:

```diff
-from scripts.seed_knowledge_base import seed
+from scripts.seed_knowledge_base import seed_knowledge_base
 
-        await seed(reset=False)
+        await seed_knowledge_base(reset=False)
 
-        await seed(reset=True)
+        await seed_knowledge_base(reset=True)
```

---

## 🟠 Altos

### A1. `agent.py` — `node_rag_answer` cria `LegalIndexer()` em cada chamada

```python
async def node_rag_answer(state: AgentState):
    indexer = LegalIndexer()  # ← Cria novo cliente ChromaDB a cada pergunta!
```

O `LegalIndexer` instancia um `PersistentClient` do ChromaDB. Criar um a cada chamada é custoso.

```diff
+# Singleton do indexer
+_legal_indexer = None
+def _get_indexer():
+    global _legal_indexer
+    if _legal_indexer is None:
+        _legal_indexer = LegalIndexer()
+    return _legal_indexer
+
 async def node_rag_answer(state: AgentState):
-    indexer = LegalIndexer()
+    indexer = _get_indexer()
```

---

### A2. `agent.py` — `node_generate_briefing` trata `ConversationState` como `LeadSchema`

```python
async def node_generate_briefing(state: AgentState):
    lead = state["conversation"]  # ← É ConversationState, não LeadSchema!
    briefing_path = await generator.generate_briefing(lead)  # ← generator espera LeadSchema
```

`DocumentGenerator.generate_briefing()` espera um `LeadSchema` (com `name`, `phone`, `email`), mas recebe um `ConversationState` (que não tem esses campos).

```diff
 async def node_generate_briefing(state: AgentState):
     generator = DocumentGenerator()
-    lead = state["conversation"]
+    # Converter ConversationState para LeadSchema (ou buscar do DB)
+    from src.models.lead import LeadSchema
+    conv = state["conversation"]
+    lead = LeadSchema(
+        id=conv.session_id,
+        name=conv.triage_answers[0].get("resposta", "N/A") if conv.triage_answers else "N/A",
+        phone="",
+        area_juridica=conv.area_juridica,
+        score=conv.score,
+        triage_data={"answers": conv.triage_answers},
+    )
```

---

### A3. `crm.py` — API key na URL (segurança)

```python
url = f"{self.base_url}/persons?api_token={self.api_token}"  # ← Token exposto em logs de URL
```

API tokens na URL aparecem em logs de servidor, histórico do navegador e proxies. Use header:

```diff
-url = f"{self.base_url}/persons?api_token={self.api_token}"
-response = await client.post(url, json=payload)
+url = f"{self.base_url}/persons"
+headers = {"Authorization": f"Bearer {self.api_token}"}
+response = await client.post(url, json=payload, headers=headers)
```

---

### A4. Channel adapters — `send_document` não implementado

`base.py` define `send_document` como abstrato, mas nenhum adapter implementa:

```python
class ChannelAdapter(ABC):
    @abstractmethod
    async def send_document(...) -> bool:  # ← Requer implementação
```

Mas `WhatsAppAdapter`, `TelegramAdapter` e `InstagramAdapter` não definem `send_document`. Isto causa `TypeError` ao instanciar.

---

## 🟡 Médios

### M1. `webhooks.py` — Router não registrado no `main.py`

O `APIRouter` é definido mas nunca incluído no app FastAPI:

```diff
 # src/main.py — adicionar:
+from src.api.webhooks import router as webhooks_router
+
 app = FastAPI(...)
+app.include_router(webhooks_router)
```

Sem isso, os endpoints `/webhooks/whatsapp` etc. não existem.

---

### M2. `webhooks.py` — `WhatsAppAdapter` instanciado no module-level

```python
whatsapp = WhatsAppAdapter()  # Linha 11 — executa no import
```

Se `settings.whatsapp_phone_number_id` estiver vazio, o `base_url` fica quebrado.

---

### M3. `transcriber.py` — Placeholder sem funcionalidade real

O transcriber retorna string hardcoded e nunca baixa o áudio. Para MVP, pelo menos baixar o arquivo e salvar localmente:

```diff
 async def transcribe_audio_from_url(audio_url: str) -> str:
-    return "[Simulação]: Cliente relatou demissão sem justa causa."
+    async with httpx.AsyncClient() as http:
+        # Baixar áudio da Meta
+        media_resp = await http.get(audio_url, headers={
+            "Authorization": f"Bearer {settings.whatsapp_api_token}"
+        })
+        temp_path = f"/tmp/audio_{hash(audio_url)}.ogg"
+        with open(temp_path, "wb") as f:
+            f.write(media_resp.content)
+        # Transcrever
+        client = AsyncOpenAI(api_key=settings.openai_api_key)
+        with open(temp_path, "rb") as audio_file:
+            response = await client.audio.transcriptions.create(
+                file=audio_file, model=settings.whisper_model
+            )
+        return response.text
```

---

### M4. `test_e2e_agent.py` — Asserts fracos

```python
assert result["next_node"] == "END" or result["next_node"] == ""  # ← Aceita vazio
assert mock_handoff.called  # ← Mas handoff nunca é chamado no fluxo real
```

O handoff mock nunca será acionado porque o nó `node_handoff` do agente não chama `HandoffManager`. O test assert vai **falhar**.

---

### M5. `flows.py` — Não integra as perguntas gerais + área-específica

O `TriageFlow` só retorna perguntas da área jurídica, mas deveria primeiro perguntar as gerais e depois as da área:

```diff
     def get_next_question(state: ConversationState) -> str:
         area = state.area_juridica or "geral"
-        questions = TRIAGE_QUESTIONS.get(area, TRIAGE_QUESTIONS["geral"])
+        # Combina perguntas gerais + área específica
+        questions = TRIAGE_QUESTIONS["geral"].copy()
+        if area != "geral" and area in TRIAGE_QUESTIONS:
+            questions.extend(TRIAGE_QUESTIONS[area])
```

---

## 🔵 Baixos

### B1. `handoff/manager.py` — Não usa `notifications.py`

O `HandoffManager` tem um comentário `# chamar integrations.notifications.send_slack(message)` mas nunca chama. Basta conectar.

### B2. `instagram.py` — API v18.0 hardcoded

Usar variável de configuração para a versão da API do Facebook.

---

## Ações Recomendadas (Prioridade)

| # | Ação | Impacto | Esforço |
|---|---|---|---|
| 1 | Corrigir `eproc.py` e `pje.py` (escapes quebrados) | 🔴 SyntaxError | 2 min |
| 2 | Adicionar validação de assinatura nos webhooks | 🔴 Segurança | 10 min |
| 3 | Corrigir imports do `test_seed.py` | 🔴 Testes quebrados | 2 min |
| 4 | Singleton do `LegalIndexer` no agent | 🟠 Performance | 3 min |
| 5 | Corrigir type mismatch `ConversationState` vs `LeadSchema` | 🟠 Crash | 5 min |
| 6 | Mover API key do Pipedrive pra header | 🟠 Segurança | 2 min |
| 7 | Implementar `send_document` nos adapters | 🟠 ABC quebrado | 5 min |
| 8 | Registrar router de webhooks no `main.py` | 🟡 Endpoints inexistentes | 1 min |
| 9 | Combinar perguntas gerais + área no `flows.py` | 🟡 Triagem incompleta | 2 min |
