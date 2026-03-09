# Configuração do Canal Telegram

Siga os passos abaixo para configurar o bot do Telegram para o Agente Jurídico Breviliere.

## 1. Criar o Bot no Telegram
1. Abra o Telegram e procure por `@BotFather`.
2. Envie o comando `/newbot`.
3. Siga as instruções para dar um nome e um username ao seu bot (ex: `BreviliereJuridicoBot`).
4. O BotFather enviará um **HTTP API Token**. Salve este token.

## 2. Configurar Variáveis de Ambiente
No seu arquivo `.env`, adicione o token obtido:
```env
TELEGRAM_BOT_TOKEN=seu_token_aqui
```

## 3. Configurar o Webhook
O Telegram precisa saber para onde enviar as mensagens recebidas.

### Localmente (com ngrok)
1. Inicie o ngrok: `ngrok http 8000`.
2. Copie a URL HTTPS gerada (ex: `https://1234.ngrok-free.app`).
3. Execute o seguinte comando `curl` para registrar o webhook:
```bash
curl -X POST "https://api.telegram.org/bot{SEU_TOKEN}/setWebhook?url={SUA_URL_NGROK}/webhooks/telegram"
```

### Produção
Substitua a URL do ngrok pelo domínio do seu servidor:
```bash
curl -X POST "https://api.telegram.org/bot{SEU_TOKEN}/setWebhook?url=https://seu-dominio.com/webhooks/telegram"
```

## 4. Testar a Integração
1. Certifique-se de que a aplicação está rodando.
2. Abra seu bot no Telegram e envie uma mensagem (ex: "Ola").
3. Verifique os logs da aplicação para confirmar o recebimento via `webhook_telegram_recebido`.
4. O bot deve responder seguindo o fluxo de consentimento LGPD e triagem.

## Health Check
Você pode verificar se o endpoint está ativo acessando:
`GET /webhooks/telegram/health`
