# Gean Clone — Bot Telegram

## Arquivos

- `gean-clone-telegram.workflow.json` — Workflow para importar no n8n.cloud

## Como configurar

### 1. Importar o workflow no n8n.cloud

1. Acesse seu n8n.cloud
2. Vá em **Workflows → Import from file**
3. Selecione `gean-clone-telegram.workflow.json`

### 2. Configurar credenciais

Após importar, o n8n vai pedir para mapear as credenciais:

**Telegram — Gean Bot:**
- Tipo: `Telegram API`
- Bot Token: (token do @BotFather)

**Anthropic — Gean:**
- Tipo: `Anthropic API`
- API Key: (chave do console.anthropic.com)

### 3. Ativar o workflow

1. Clique em **Activate** (toggle no canto superior direito)
2. O webhook do Telegram será registrado automaticamente

### 4. Testar

Envie uma mensagem para o bot no Telegram e verifique a resposta.

---

## Estrutura do Workflow

```
Telegram Trigger
    ↓
Filtro (só texto)
    ↓
Gean Agent (Claude Sonnet 4.6)
    ├── Claude Sonnet 4.6 (LLM)
    └── Memória da Conversa (15 mensagens por sessão)
    ↓
Enviar Resposta (Telegram)
```

## Ajustes comuns

| O que ajustar | Onde |
|---------------|------|
| Tom do personagem | Node "Gean Agent" → System Message |
| Tamanho da memória | Node "Memória da Conversa" → Context Window Length |
| Modelo Claude | Node "Claude Sonnet 4.6" → Model |
| Comprimento da resposta | Node "Claude Sonnet 4.6" → Max Tokens |
