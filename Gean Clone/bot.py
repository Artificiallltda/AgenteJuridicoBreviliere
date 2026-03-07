import json
import logging
import os
import uuid

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import gmail_client
from core.graph import process_message

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─── Configuração ─────────────────────────────────────────────────────────────

DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ADMIN_CHAT_ID = int(os.environ["TELEGRAM_ADMIN_CHAT_ID"])

GMAIL_USER = os.environ["GMAIL_USER_EMAIL"]
GOOGLE_CREDS = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])

EMAIL_POLL_INTERVAL = int(os.environ.get("EMAIL_POLL_INTERVAL", "120"))

# ─── State (email approval — Telegram-specific) ───────────────────────────────

pending_emails: dict[str, dict] = {}
editing_state: dict[int, str] = {}

# ─── Email generation (DeepSeek direto — sem passar pelo graph) ───────────────

EMAIL_SYSTEM_PROMPT = """Você é Gean Santos 🇮🇹 — CEO da Artificiall Ltda. Escreva uma resposta profissional mas com o tom informal e direto do Gean para o email abaixo.

REGRAS:
- Escreva APENAS o corpo da resposta, sem assunto nem saudação formal
- Tom informal mas respeitoso — como o Gean realmente escreve
- Direto ao ponto, sem enrolação
- Em português, a menos que o email original seja em outro idioma
- Não use markdown nem formatação especial
- NÃO assine o email, a assinatura será adicionada automaticamente"""

EMAIL_SIGNATURE = """
--
Gean Santos
CEO | Artificiall Ltda
artificiall.ai | artificiallcorporate.org"""


def generate_email_reply(email: dict) -> str:
    prompt = (
        f"De: {email['sender']}\n"
        f"Assunto: {email['subject']}\n\n"
        f"{email['body']}"
    )
    messages = [
        {"role": "system", "content": EMAIL_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    response = requests.post(
        DEEPSEEK_URL,
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": DEEPSEEK_MODEL,
            "messages": messages,
            "max_tokens": 1024,
            "temperature": 0.8,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"] + EMAIL_SIGNATURE


# ─── Telegram Handlers ────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🇮🇹 Oi! Gean aqui. O que posso fazer por você?")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    chat_id = update.effective_chat.id
    text = update.message.text

    # Modo de edição de email (Telegram-specific)
    if chat_id in editing_state:
        approval_id = editing_state.pop(chat_id)
        if approval_id in pending_emails:
            pending_emails[approval_id]["reply"] = text
            await _send_approval_message(context.bot, approval_id)
        return

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    try:
        reply = await process_message(str(chat_id), text, "telegram")
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        await update.message.reply_text("Perae que já vejo isso 🤨")


# ─── Email Approval (Telegram inline buttons) ─────────────────────────────────

async def _send_approval_message(bot, approval_id: str) -> None:
    email = pending_emails[approval_id]
    sender_display = email["sender"].split("<")[0].strip() or email["sender"]

    text = (
        f"📧 Email novo de: {sender_display}\n"
        f"Assunto: {email['subject']}\n\n"
        f"{email['body'][:500]}{'...' if len(email['body']) > 500 else ''}\n\n"
        f"─────────────────\n"
        f"✍️ Resposta gerada:\n\n"
        f"{email['reply']}"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Enviar", callback_data=f"send_{approval_id}"),
            InlineKeyboardButton("✏️ Editar", callback_data=f"edit_{approval_id}"),
            InlineKeyboardButton("❌ Cancelar", callback_data=f"cancel_{approval_id}"),
        ]
    ])

    await bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=text,
        reply_markup=keyboard,
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_", 1)
    action, approval_id = parts[0], parts[1]

    if approval_id not in pending_emails:
        await query.edit_message_text("⚠️ Esse email já foi processado.")
        return

    email = pending_emails[approval_id]

    if action == "send":
        try:
            svc = gmail_client.get_service(GOOGLE_CREDS, GMAIL_USER)
            gmail_client.send_reply(svc, email, email["reply"])
            del pending_emails[approval_id]
            await query.edit_message_text(
                f"✅ Resposta enviada para {email['sender'].split('<')[0].strip()}"
            )
        except Exception as e:
            logger.error(f"Erro ao enviar email: {e}")
            await query.edit_message_text(f"❌ Erro ao enviar: {e}")

    elif action == "edit":
        editing_state[ADMIN_CHAT_ID] = approval_id
        await query.edit_message_text(
            f"✏️ Manda a nova resposta para o email de:\n{email['sender']}\n\nAssunto: {email['subject']}"
        )

    elif action == "cancel":
        del pending_emails[approval_id]
        await query.edit_message_text("❌ Resposta cancelada.")


# ─── Job: Polling de Emails ───────────────────────────────────────────────────

async def check_emails_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        svc = gmail_client.get_service(GOOGLE_CREDS, GMAIL_USER)
        emails = gmail_client.get_unread_emails(svc, max_results=5)

        for email in emails:
            approval_id = str(uuid.uuid4())[:8]

            try:
                reply = generate_email_reply(email)
            except Exception as e:
                logger.error(f"Erro ao gerar reply de email: {e}")
                reply = "Vou verificar e te retorno em breve."

            pending_emails[approval_id] = {**email, "reply": reply}
            gmail_client.mark_as_read(svc, email["id"])
            await _send_approval_message(context.bot, approval_id)

    except Exception as e:
        logger.error(f"Erro no polling de emails: {e}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.job_queue.run_repeating(
        check_emails_job,
        interval=EMAIL_POLL_INTERVAL,
        first=15,
    )

    logger.info("Bot do Gean iniciado com multi-agentes LangGraph...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
