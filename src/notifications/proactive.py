from src.config.logging import get_logger
from src.models.conversation import ConversationState

logger = get_logger(__name__)

class ProactiveNotifier:
    def __init__(self, adapters: dict):
        """
        Inicializa o notificador com os adaptadores de canal.
        Ex: {"whatsapp": whatsapp_adapter, "telegram": telegram_adapter}
        """
        self.adapters = adapters

    async def send_followup(self, session_id: str, channel: str, message: str) -> bool:
        """Envia uma mensagem de followup para um usuario especifico."""
        adapter = self.adapters.get(channel.lower())
        if not adapter:
            logger.error("canal_nao_suportado_para_followup", channel=channel, session_id=session_id)
            return False

        try:
            logger.info("enviando_followup_proativo", session_id=session_id, channel=channel)
            await adapter.send_text(session_id, message)
            return True
        except Exception as e:
            logger.error("falha_envio_followup", session_id=session_id, error=str(e))
            return False

    async def check_abandoned_sessions(self, sessions: dict, timeout_minutes: int = 30) -> list:
        """
        Identifica sessoes que pararam no meio do fluxo.
        Como o history nao tem timestamp, seguimos a regra: len(history) > 2 e step == 'triage'.
        """
        abandoned_ids = []
        for session_id, state in sessions.items():
            # Regra simplificada conforme requisito
            if state.current_step == "triage" and len(state.history) > 2:
                abandoned_ids.append(session_id)
        
        logger.info("verificacao_sessoes_abandonadas", total_encontrado=len(abandoned_ids))
        return abandoned_ids

    def get_followup_message(self, step: str, area: str = None) -> str:
        """Retorna uma mensagem de followup baseada no passo atual."""
        messages = {
            "init": "Ola! Vi que voce iniciou um atendimento mas nao continuou. Posso ajudar?",
            "triage": "Notei que ficaram algumas perguntas pendentes. Gostaria de continuar de onde paramos?",
            "briefing": "Seu briefing esta quase pronto! Gostaria de finalizar?",
        }
        return messages.get(step, "Ola! Como posso ajudar voce hoje?")
