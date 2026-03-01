from src.integrations.notifications import send_slack_notification
from src.config.logging import get_logger

logger = get_logger(__name__)


class HandoffManager:
    """Gerencia a transferencia de conversas da IA para atendimento humano."""

    async def request_handoff(self, session_id: str, channel: str, briefing: str) -> bool:
        """Solicita handoff para equipe humana.

        Args:
            session_id: ID da sessao da conversa
            channel: Canal de origem (whatsapp, telegram, instagram)
            briefing: Resumo do atendimento ate o momento

        Returns:
            True se a notificacao foi enviada com sucesso.
        """
        logger.info("handoff_solicitado", session_id=session_id, channel=channel)

        message = (
            f"*Novo atendimento para handoff humano*\n"
            f"Sessao: {session_id}\n"
            f"Canal: {channel}\n\n"
            f"{briefing}"
        )

        result = await send_slack_notification(message)

        if result:
            logger.info("handoff_notificacao_enviada", session_id=session_id)
        else:
            logger.warning("handoff_notificacao_falhou", session_id=session_id)

        return result
