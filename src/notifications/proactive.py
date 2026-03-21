"""
ProactiveNotifier — Envia mensagens proativas de followup para clientes.

Usado para:
- Followup de sessoes abandonadas
- Notificacoes proativas de atualizacoes
- Campanhas de re-engajamento
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from config.logging import get_logger

logger = get_logger(__name__)


class ProactiveNotifier:
    """Gerencia o envio de mensagens proativas para clientes."""

    def __init__(self, adapters: Dict[str, Any]):
        """
        Inicializa o notifier com os adapters de canal.
        
        Args:
            adapters: Dicionario com adapters por canal (whatsapp, telegram, instagram)
        """
        self.adapters = adapters
        logger.info("proactive_notifier_inicializado")

    def get_followup_message(self, current_step: str, area_juridica: str = None) -> str:
        """
        Gera mensagem de followup baseada no estado da conversa.
        
        Args:
            current_step: Etapa atual da conversa (triage, briefing, handoff, etc.)
            area_juridica: Area juridica do caso (opcional)
            
        Returns:
            Mensagem de followup personalizada
        """
        messages = {
            "triage": (
                "Olá! 👋 Vi que você iniciou o atendimento "
                "mas ainda temos perguntas pendentes. Podemos continuar? "
                "Estou aqui para te ajudar!"
            ),
            "briefing": (
                "Olá! Seu caso já foi analisado pela nossa equipe. 📋 "
                "Em breve um advogado especialista entrará em contato. "
                "Fique atento(a) ao telefone!"
            ),
            "handoff": (
                "Olá! Seu atendimento já foi encaminhado para um advogado. ⚖️ "
                "Ele entrará em contato em até 24 horas úteis. "
                "Precisando de algo, estamos à disposição!"
            ),
            "rag": (
                "Olá! Ficou alguma dúvida sobre as informações que enviei? 🤔 "
                "Posso te ajudar com mais alguma coisa?"
            )
        }

        base_message = messages.get(current_step, messages["triage"])

        # Adiciona personalizacao por area se disponivel
        if area_juridica:
            area_messages = {
                "trabalhista": " (especialista em Direito Trabalhista)",
                "familia": " (especialista em Direito de Família)",
                "criminal": " (especialista em Direito Criminal)",
                "previdenciario": " (especialista em Direito Previdenciário)",
                "civil": " (especialista em Direito Civil)"
            }
            area_suffix = area_messages.get(area_juridica.lower(), "")
            if area_suffix:
                base_message = base_message.replace("advogado", f"advogado{area_suffix}")

        return base_message

    async def send_followup(self, session_id: str, channel: str, message: str) -> bool:
        """
        Envia mensagem de followup para uma sessao especifica.
        
        Args:
            session_id: ID da sessao (channel_user_id)
            channel: Canal de comunicacao (whatsapp, telegram, instagram)
            message: Mensagem a ser enviada
            
        Returns:
            True se enviado com sucesso, False caso contrario
        """
        try:
            adapter = self.adapters.get(channel)
            if not adapter:
                logger.error("adapter_nao_encontrado", channel=channel)
                return False

            success = await adapter.send_text(session_id, message)
            
            if success:
                logger.info("followup_enviado", session_id=session_id, channel=channel)
            else:
                logger.warning("followup_falhou", session_id=session_id, channel=channel)
            
            return success

        except Exception as e:
            logger.error("erro_enviar_followup", session_id=session_id, error=str(e))
            return False

    async def check_abandoned_sessions(
        self,
        sessions: Dict,
        timeout_minutes: int = 30
    ) -> List[str]:
        """
        Identifica sessoes abandonadas (sem atividade por X minutos).
        
        Args:
            sessions: Dicionario de sessoes ativas
            timeout_minutes: Tempo minimo sem atividade para considerar abandonada
            
        Returns:
            Lista de session_ids abandonadas
        """
        abandoned = []
        now = datetime.now()

        for session_id, state in sessions.items():
            # Verifica se a sessao tem historico e se esta em passo intermediario
            if not hasattr(state, 'history') or not state.history:
                continue

            # Sessoes em 'closed' ou 'rag' nao sao consideradas abandonadas
            if hasattr(state, 'current_step') and state.current_step in ['closed', 'rag']:
                continue

            # Pega o timestamp da ultima mensagem (se disponivel no historico)
            last_message_time = None
            for msg in reversed(state.history):
                if isinstance(msg, dict) and 'timestamp' in msg:
                    last_message_time = msg['timestamp']
                    break

            # Se nao tem timestamp, usa logica simples de contagem de mensagens
            if last_message_time is None:
                # Assume que sessoes com 2-5 mensagens e paradas em triage sao abandonadas
                if len(state.history) >= 2 and len(state.history) <= 5:
                    if hasattr(state, 'current_step') and state.current_step == 'triage':
                        abandoned.append(session_id)
            else:
                # Compara tempo de inatividade
                if isinstance(last_message_time, datetime):
                    inactive_time = now - last_message_time
                    if inactive_time > timedelta(minutes=timeout_minutes):
                        abandoned.append(session_id)

        logger.info(
            "sessoes_abandonadas_detectadas",
            count=len(abandoned),
            timeout_minutes=timeout_minutes
        )

        return abandoned

    async def send_batch_notifications(
        self,
        recipients: List[Dict[str, str]],
        message: str
    ) -> Dict[str, int]:
        """
        Envia notificacoes em lote para multiplos destinatarios.
        
        Args:
            recipients: Lista de dicts com 'session_id' e 'channel'
            message: Mensagem a ser enviada
            
        Returns:
            Dict com contagem de enviados e falhas
        """
        sent = 0
        failed = 0

        for recipient in recipients:
            session_id = recipient.get('session_id')
            channel = recipient.get('channel', 'whatsapp')

            success = await self.send_followup(session_id, channel, message)
            if success:
                sent += 1
            else:
                failed += 1

        return {"sent": sent, "failed": failed}
