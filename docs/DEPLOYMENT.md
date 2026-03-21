# Guia de Deployment — Agente Jurídico (Breviliere)

Este documento descreve os passos para colocar o sistema em produção com foco em segurança, escalabilidade e conformidade.

## 🏢 Arquitetura de Produção Proposta

### Infraestrutura de Rede
- **Frontend/Webhooks:** Nginx (Proxy Reverso) + Certbot (SSL)
- **Runtime:** Gunicorn/Uvicorn em containers Docker
- **Banco de Dados:** PostgreSQL 16 (RDS ou self-hosted)
- **Mensageria:** Redis 7 para sessões e filas
- **Vector DB:** Qdrant Cloud (recomendado para prod) ou ChromaDB robusto

---

## 🛠️ Passo a Passo do Deploy

### 1. Configuração da Meta Cloud API (WhatsApp/Instagram)
Para que o agente funcione em produção, siga estes passos no [Meta for Developers](https://developers.facebook.com/):
1. **App Type:** Business
2. **Produtos:** WhatsApp, Instagram Messaging
3. **Webhook URL:** `https://seu-dominio.com/webhooks/whatsapp`
4. **Verify Token:** Deve ser o mesmo definido em `WHATSAPP_VERIFY_TOKEN` no `.env`.
5. **Configurar Webhooks:** Ative os campos `messages` em `WhatsApp Business Account`.

### 2. Configuração de DNS e HTTPS
Aponte seu domínio para o IP do servidor e configure o Nginx:
```nginx
server {
    listen 80;
    server_name seu-dominio.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name seu-dominio.com;
    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. CI/CD com GitHub Actions
O projeto está preparado para deploy automático via `ci.yml`. Certifique-se de configurar os **Secrets** no GitHub:
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD`
- `SSH_PRIVATE_KEY`
- `PRODUCTION_ENV_FILE`

### 4. Segurança de Segredos (HashiCorp Vault)
Em produção, não utilize `.env` diretamente para chaves sensíveis. Utilize o **HashiCorp Vault** ou **AWS Secrets Manager**:
- Integre o `src/config/settings.py` com o provedor de segredos escolhido.
- Certifique-se de que o certificado OAB (A1) do advogado está no Vault.

---

## 🛡️ Hardening e Conformidade LGPD
- **Rate Limiting:** Ative o middleware de rate limiting para evitar ataques de força bruta no webhook.
- **Auditoria:** Certifique-se de que os logs estruturados (`structlog`) estão sendo enviados para um log aggregator (Datadog/Grafana Loki).
- **Expurgo:** Configure o cron job de limpeza de dados após o período de retenção jurídica (5 anos).
