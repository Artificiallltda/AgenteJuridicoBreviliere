# Configuracao do Canal Instagram

Siga os passos abaixo para conectar o Instagram Business ao Agente Juridico Breviliere.

## 1. Requisitos no Facebook/Meta
1. Voce deve ter uma **Pagina no Facebook**.
2. Uma conta do **Instagram Business** (ou Creator) vinculada a essa Pagina.
3. No App do Instagram: `Configuracoes > Mensagens e respostas a stories > Ferramentas de mensagens > Permitir acesso a mensagens` (Habilitar).

## 2. Criar App no Meta Developer Portal
1. Acesse [developers.facebook.com](https://developers.facebook.com).
2. Crie um novo App do tipo "Negocios" (Business).
3. Adicione o produto **Instagram Graph API**.

## 3. Configurar Mensagens
1. Va em `Instagram > Basic Setup`.
2. Conecte sua Pagina do Facebook e a conta do Instagram vinculada.
3. Gere o **INSTAGRAM_ACCESS_TOKEN** (Page Access Token com as permissoes corretas).

## 4. Configurar Webhook
1. Em `Webhooks`, selecione `Instagram` no menu suspenso.
2. Clique em `Edit Subscription`.
3. **URL de retorno**: `{URL_DO_SERVIDOR}/webhooks/instagram`
4. **Token de verificacao**: O mesmo valor definido em `WHATSAPP_VERIFY_TOKEN` no seu `.env`.
5. Em `Subscription Fields`, assine pelo menos: `messages`, `messaging_postbacks`.

## 5. Permissoes (Review do App)
Para producao, voce precisara solicitar as permissoes:
- `instagram_manage_messages`
- `pages_manage_metadata`
- `pages_messaging`

## 6. Variaveis de Ambiente
Atualize seu `.env`:
```env
INSTAGRAM_ACCESS_TOKEN=seu_token_aqui
WHATSAPP_VERIFY_TOKEN=mesmo_token_meta
```

## 7. Testar
Envie um Direct Message para o perfil do Instagram Business. O bot deve responder seguindo o fluxo de atendimento.
Para audios, o bot usara a API de midia da Meta para transcrever automaticamente.
