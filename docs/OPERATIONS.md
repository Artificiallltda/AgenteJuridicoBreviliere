# Guia de Operação — Agente Jurídico (Breviliere)

Este documento descreve as rotinas operacionais para manter o **Agente Jurídico (Breviliere)** atualizado e saudável.

## 📚 Gestão da Base de Conhecimento (RAG)

O sistema utiliza a pasta `knowledge_base/` como fonte de verdade jurídica.

### 1. Adicionar Novo Conteúdo
Para atualizar o conhecimento do agente (ex: nova súmula ou FAQ):
1.  Crie ou edite um arquivo `.md` na pasta correspondente (`faq/`, `institucional/`, `jurisprudencia/`).
2.  Use o separador `###` para dividir as perguntas e respostas.
3.  Execute o script de indexação:
    ```bash
    uv run python scripts/seed_knowledge_base.py
    ```
    *Dica: Use `--reset` para reconstruir a base do zero se houver muitas alterações.*

### 2. Formato do FAQ
O script de indexação (`seed_knowledge_base.py`) é sensível ao formato:
```markdown
### Pergunta do Cliente?
Resposta do Escritório Breviliere Advocacia...
```

---

## 📈 Monitoramento e Logs

O sistema utiliza **Logs Estruturados** (`structlog`) para facilitar a depuração.

### 1. Monitorar em Tempo Real (Docker)
Para ver o que está acontecendo agora no app:
```bash
docker compose -f docker/docker-compose.yml logs -f app
```

### 2. Identificar Sessões e Canais
Procure pelos campos `session_id` e `channel` nos logs JSON para rastrear o fluxo de um cliente específico.
```json
{"event": "webhook_whatsapp_recebido", "session_id": "5511999999999", "channel": "whatsapp"}
```

---

## 📱 Configurar Novos Canais

### 1. Telegram
1.  Fale com o [@BotFather](https://t.me/botfather) e obtenha o `TELEGRAM_BOT_TOKEN`.
2.  Adicione o token ao `.env`.
3.  Configure o webhook do Telegram via comando `curl`:
    ```bash
    curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://seu-dominio.com/webhooks/telegram"
    ```

### 2. Instagram
1.  Certifique-se de que sua conta Instagram está vinculada a uma Página do Facebook.
2.  Obtenha o `INSTAGRAM_ACCESS_TOKEN` no Meta for Developers.
3.  Adicione o token ao `.env` e configure o webhook na plataforma Meta.

---

## 🚨 Troubleshooting Comum

| Sintoma | Possível Causa | Solução |
|---|---|---|
| IA responde fora da base | Alucinação ou falta de contexto | Verifique se os arquivos em `knowledge_base/` foram indexados com o script de seed. |
| Webhook da Meta falha | Token de verificação incorreto | Verifique `WHATSAPP_VERIFY_TOKEN` no `.env` e no console da Meta. |
| Erro de Conexão DB | Container Postgres desligado | Execute `docker compose up -d` para reativar a infraestrutura. |
| Erro ao Gerar Documento | Template DOCX corrompido ou ausente | Verifique se `src/documents/templates/briefing.docx` existe e é válido. |

---

## ⚖️ Sigilo e Segurança
Este sistema manipula dados sensíveis. Nunca compartilhe arquivos de logs brutos ou o arquivo `.env` com terceiros não autorizados. Realize auditorias periódicas nas sessões para garantir a conformidade com a LGPD.
