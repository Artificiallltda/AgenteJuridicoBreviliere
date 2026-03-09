from src.integrations.notifications import send_slack_notification
from src.integrations.crm import CRMIntegration
from src.integrations.pipedrive import create_deal, add_note
from src.integrations.clickup import ClickUpIntegration
from src.models.lead import LeadSchema, LeadStatus
from src.models.conversation import ConversationState
from src.config.logging import get_logger

logger = get_logger(__name__)

class HandoffManager:
    """Gerencia a transferência de conversas da IA para atendimento humano e integra com CRM e ClickUp."""

    def __init__(self):
        self.crm = CRMIntegration()
        self.clickup = ClickUpIntegration()

    async def create_crm_lead(self, state: ConversationState) -> str:
        """Converte estado da conversa em Lead no CRM."""
        try:
            # Encontra o nome nas respostas de triagem
            name = "Lead " + state.session_id
            for ans in state.triage_answers:
                if ans.get("id") == "nome":
                    name = ans.get("resposta")
                    break

            lead = LeadSchema(
                id=state.session_id,
                name=name,
                phone=state.session_id, # Usando session_id como fone se channel_user_id nao estiver explicito
                area_juridica=state.area_juridica,
                status=LeadStatus.QUALIFIED,
                score=state.score,
                triage_data={"answers": state.triage_answers, "area": state.area_juridica},
                lgpd_consent=state.lgpd_consent
            )
            
            # Cria Person
            person_id = await self.crm.create_lead(lead)
            if not person_id:
                return None
            
            # Cria Deal (Negocio)
            deal_id = await create_deal(
                self.crm, 
                person_id, 
                f"Atendimento Juridico - {name} ({state.area_juridica})"
            )
            
            # Adiciona nota com briefing
            if deal_id:
                briefing_text = "\n".join([f"Q: {a['pergunta']} | R: {a['resposta']}" for a in state.triage_answers])
                await add_note(self.crm, deal_id, f"Briefing de Triagem:\n{briefing_text}")
                return deal_id
            
            return person_id
        except Exception as e:
            logger.error("erro_integracao_crm_handoff", error=str(e))
            return None

    async def request_handoff(self, state: ConversationState, briefing: str) -> bool:
        """Solicita handoff para equipe humana via Slack e CRM."""
        session_id = state.session_id
        channel = state.channel.value if hasattr(state.channel, "value") else str(state.channel)
        
        logger.info("handoff_solicitado", session_id=session_id, channel=channel)

        # Integracao CRM
        crm_id = await self.create_crm_lead(state)
        crm_info = f"CRM ID: {crm_id}" if crm_id else "CRM: nao foi possivel criar lead"

        message = (
            f"*Novo atendimento para handoff humano*\n"
            f"Sessao: {session_id}\n"
            f"Canal: {channel}\n"
            f"{crm_info}\n\n"
            f"{briefing}"
        )

        result = await send_slack_notification(message)

        # Criação de tarefa no ClickUp para acompanhamento do lead
        name = next((a["resposta"] for a in state.triage_answers if a.get("id") == "nome"), "Lead")
        lead_for_clickup = LeadSchema(
            id=state.session_id,
            name=name,
            phone=getattr(state, "channel_user_id", state.session_id),
            area_juridica=state.area_juridica,
            score=state.score,
            triage_data={"answers": state.triage_answers},
            lgpd_consent=state.lgpd_consent
        )
        clickup_task_id = await self.clickup.create_lead_task(lead_for_clickup, briefing)
        if clickup_task_id:
            logger.info("clickup_task_criada_no_handoff", task_id=clickup_task_id, session_id=session_id)

        if result:
            logger.info("handoff_notificacao_enviada", session_id=session_id)
        else:
            logger.warning("handoff_notificacao_falhou", session_id=session_id)

        return result
