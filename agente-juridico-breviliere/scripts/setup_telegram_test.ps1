# ============================================
# Setup Automatico - Teste Telegram
# Agente Juridico Breviliere
# ============================================
# USO: .\scripts\setup_telegram_test.ps1
# ============================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Agente Juridico Breviliere - Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Coletar dados do usuario
Write-Host "[1/5] Coletando suas credenciais..." -ForegroundColor Yellow
Write-Host ""

$OPENAI_KEY = Read-Host "Cole sua OPENAI_API_KEY (sk-...)"
if (-not $OPENAI_KEY) { Write-Host "ERRO: API key obrigatoria!" -ForegroundColor Red; exit 1 }

$TELEGRAM_TOKEN = Read-Host "Cole seu TELEGRAM_BOT_TOKEN (do BotFather)"
if (-not $TELEGRAM_TOKEN) { Write-Host "ERRO: Token obrigatorio!" -ForegroundColor Red; exit 1 }

$SLACK_URL = Read-Host "Cole seu SLACK_WEBHOOK_URL (ou Enter para pular)"
if (-not $SLACK_URL) { $SLACK_URL = "https://hooks.slack.com/services/PLACEHOLDER" }

# 2. Criar .env
Write-Host ""
Write-Host "[2/5] Criando arquivo .env..." -ForegroundColor Yellow

$envContent = @"
# App Configuration
APP_NAME=Agente Juridico Breviliere
DEBUG=True
LOG_LEVEL=DEBUG

# LLM Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=$OPENAI_KEY
OPENAI_MODEL=gpt-4o
OPENAI_MODEL_LIGHT=gpt-4o-mini

# Embeddings / Vector Store
EMBEDDING_MODEL=text-embedding-3-small
CHROMA_PERSIST_DIR=./data/chroma

# Database (nao usado no MVP, placeholder)
DATABASE_URL=postgresql+asyncpg://juridico:juridico_dev@localhost:5432/juridico
REDIS_URL=redis://localhost:6379/0

# Channels
WHATSAPP_VERIFY_TOKEN=test-token
WHATSAPP_API_TOKEN=placeholder
WHATSAPP_PHONE_NUMBER_ID=placeholder
TELEGRAM_BOT_TOKEN=$TELEGRAM_TOKEN
INSTAGRAM_ACCESS_TOKEN=placeholder

# Integrations
CRM_PROVIDER=pipedrive
CRM_API_TOKEN=placeholder
SLACK_WEBHOOK_URL=$SLACK_URL
NOTIFICATION_EMAIL=teste@breviliere.com.br

# Whisper
WHISPER_MODEL=whisper-1

# LGPD
PRIVACY_POLICY_URL=https://breviliere.com.br/privacidade
TERMS_OF_USE_URL=https://breviliere.com.br/termos
DATA_RETENTION_DAYS=1825

# Meta
META_API_VERSION=v18.0
"@

$envContent | Out-File -FilePath ".env" -Encoding utf8
Write-Host "  .env criado com sucesso!" -ForegroundColor Green

# 3. Instalar dependencias
Write-Host ""
Write-Host "[3/5] Instalando dependencias Python..." -ForegroundColor Yellow
pip install -r requirements.txt 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  AVISO: pip falhou. Tente: python -m pip install -r requirements.txt" -ForegroundColor Red
}
Write-Host "  Dependencias instaladas!" -ForegroundColor Green

# 4. Verificar ngrok
Write-Host ""
Write-Host "[4/5] Verificando ngrok..." -ForegroundColor Yellow
$ngrokPath = Get-Command ngrok -ErrorAction SilentlyContinue
if (-not $ngrokPath) {
    Write-Host "  ngrok nao encontrado. Instalando via npm..." -ForegroundColor Yellow
    npm install -g ngrok 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  AVISO: Instale manualmente: https://ngrok.com/download" -ForegroundColor Red
    }
} else {
    Write-Host "  ngrok encontrado!" -ForegroundColor Green
}

# 5. Instrucoes finais
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  SETUP COMPLETO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Agora execute esses 3 comandos em terminais SEPARADOS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Terminal 1 (app):" -ForegroundColor Yellow
Write-Host "    uvicorn src.main:app --host 0.0.0.0 --port 8000" -ForegroundColor White
Write-Host ""
Write-Host "  Terminal 2 (ngrok):" -ForegroundColor Yellow
Write-Host "    ngrok http 8000" -ForegroundColor White
Write-Host ""
Write-Host "  Terminal 3 (registrar webhook - substitua a URL do ngrok):" -ForegroundColor Yellow
Write-Host "    curl -X POST `"https://api.telegram.org/bot$TELEGRAM_TOKEN/setWebhook?url=SUA_URL_NGROK/webhooks/telegram`"" -ForegroundColor White
Write-Host ""
Write-Host "Depois e so abrir o bot no Telegram e mandar 'Oi'!" -ForegroundColor Cyan
Write-Host ""
