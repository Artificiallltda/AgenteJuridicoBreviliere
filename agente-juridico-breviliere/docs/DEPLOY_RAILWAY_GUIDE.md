# Guia de Deploy no Railway (Nuvem 24/7)

Este guia descreve os passos para hospedar o **Agente Jurídico Breviliere** na nuvem usando o [Railway](https://railway.app), permitindo que ele funcione 24 horas por dia, 7 dias por semana, sem depender da sua máquina local.

## Passo 1: Conectar o GitHub no Railway

1. Acesse [railway.app](https://railway.app) e faça login (recomendado usar a sua conta do GitHub).
2. Clique no botão **"New Project"** (ou "Start a New Project").
3. Escolha a opção **"Deploy from GitHub repo"**.
4. Procure e selecione o seu repositório: `Artificiallltda/AgenteJuridicoBreviliere`.
5. O Railway detectará automaticamente que é um projeto Python (FastAPI/Uvicorn) através do `requirements.txt` / `Dockerfile` e começará a preparar o ambiente.

## Passo 2: Adicionar as Variáveis de Ambiente (O Segredo!)

Assim que o projeto carregar na tela do Railway, o primeiro deploy provavelmente vai falhar porque o sistema ainda não tem as suas chaves de API (que não sobem para o GitHub por segurança).

1. Clique no card do seu aplicativo na tela principal do seu projeto no Railway.
2. Navegue até a aba **"Variables"** (Variáveis).
3. Em **Variables** (Variáveis), adicione as chaves de API necessárias para o bot rodar.
   - `OPENAI_API_KEY` (Sua chave da OpenAI, ex: `fake-api-key-aqui`)
   - `WHATSAPP_VERIFY_TOKEN` (Se usar Meta API)
   - `TELEGRAM_BOT_TOKEN` (Se usar Telegram)
   - `WHATSAPP_API_TOKEN` (Se for usar o WhatsApp)
   - `CRM_PROVIDER` (pipedrive) e `CRM_API_TOKEN` (O token do Pipedrive)
   - *As URLs de banco de dados (`DATABASE_URL`) e redis (`REDIS_URL`) podem ficar com os valores do `.env.example` por enquanto se você não for usá-los em produção imediatamente.*

## Passo 3: Gerar Domínio e Atualizar Webhooks

Para que o Telegram, WhatsApp e Instagram consigam mandar mensagens para o seu agente, eles precisam do endereço web público dele.

1. No painel do seu app no Railway, vá para a aba **"Settings"** (Configurações).
2. Role a página até encontrar a seção **"Networking"** ou **"Domains"**.
3. Clique no botão **"Generate Domain"**. 
4. O Railway criará uma URL pública, segura (HTTPS) e gratuita para o seu projeto. Exemplo: `https://agentejuridico-production.up.railway.app`.

### Atualizando os Webhooks:

**Para o Telegram:**
Copie a URL abaixo, substitua pelo seu token e pelo domínio do Railway, e cole no seu navegador:
```text
https://api.telegram.org/bot<SEU_TOKEN_DO_TELEGRAM>/setWebhook?url=https://<SEU_DOMINIO_GERADO_NO_RAILWAY>/webhooks/telegram
```
Se retornar `{"ok":true,"result":true,"description":"Webhook was set"}`, funcionou!

**Para o WhatsApp / Instagram (Meta):**
1. Vá até o [Painel de Desenvolvedor da Meta](https://developers.facebook.com/).
2. Nas configurações do WhatsApp > Configuração, edite o "Webhook".
3. Em *URL de Retorno* (Callback URL), cole: `https://<SEU_DOMINIO_GERADO_NO_RAILWAY>/webhooks/whatsapp`
4. Em *Token de Verificação* (Verify Token), cole o valor da sua variável `WHATSAPP_VERIFY_TOKEN`.
5. Clique em Verificar e Salvar.

## E depois?

O seu agente agora está online 24/7! 

* **Atualizações de Código:** Sempre que você mudar algo no código na sua máquina e der um `git push` para o GitHub, o Railway vai perceber a mudança na mesma hora (auto-deploy) e atualizar o sistema sozinho em alguns minutos.
* **Logs:** Você pode ver tudo o que o agente está pensando e os erros diretamente na aba **"Deployments" -> "View Logs"** no Railway.
