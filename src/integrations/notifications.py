import httpx
from config.settings import get_settings
from config.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


async def send_slack_notification(message: str) -> bool:
    """Envia notificacao via Slack webhook."""
    webhook_url = getattr(settings, "slack_webhook_url", "")
    if not webhook_url:
        logger.warning("slack_webhook_nao_configurado")
        return False

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json={"text": message})
            if response.status_code == 200:
                logger.info("notificacao_slack_enviada")
                return True
            else:
                logger.error("erro_envio_slack", status=response.status_code)
                return False
    except Exception as e:
        logger.error("erro_envio_slack", error=str(e))
        return False


async def send_email_notification(to: str, subject: str, body: str) -> bool:
    """Envia notificacao via e-mail (placeholder para integrar com SMTP/SendGrid)."""
    logger.info("email_notificacao_solicitada", to=to, subject=subject)
    # TODO: Integrar com SMTP ou SendGrid
    return True
