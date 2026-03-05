"""
ClickUp Integration — Cria tarefas automaticamente ao fazer handoff.

Quando um lead qualificado é encaminhado para um advogado,
uma tarefa é criada no ClickUp com o briefing completo do cliente.
"""

import httpx
from src.config.settings import get_settings
from src.config.logging import get_logger
from src.models.lead import LeadSchema

logger = get_logger(__name__)
settings = get_settings()

CLICKUP_BASE_URL = "https://api.clickup.com/api/v2"


class ClickUpIntegration:
    """Integração com ClickUp para gestão de leads e handoffs."""

    def __init__(self):
        self.api_token = settings.clickup_api_token
        self.list_id = settings.clickup_list_id
        self.enabled = bool(self.api_token and self.list_id)

        if not self.enabled:
            logger.warning("clickup_desabilitado", reason="CLICKUP_API_TOKEN ou CLICKUP_LIST_ID não configurados")

    async def create_lead_task(self, lead: LeadSchema, briefing: str) -> str | None:
        """
        Cria uma tarefa no ClickUp ao receber um novo lead qualificado.
        Retorna o ID da tarefa criada, ou None em caso de erro.
        """
        if not self.enabled:
            logger.info("clickup_task_ignorada", reason="integração desabilitada")
            return None

        # Define prioridade baseada no score do lead
        priority = self._get_priority(lead.score)

        # Conteúdo da tarefa
        task_name = f"Novo Lead: {lead.name} | {lead.area_juridica or 'Área não identificada'}"
        description = self._build_task_description(lead, briefing)

        payload = {
            "name": task_name,
            "description": description,
            "priority": priority,
            "tags": ["lead", "bot-breviliere", lead.area_juridica or "geral"],
            "custom_fields": [
                {"id": "score", "value": str(lead.score)}
            ] if lead.score else []
        }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    f"{CLICKUP_BASE_URL}/list/{self.list_id}/task",
                    headers={
                        "Authorization": self.api_token,
                        "Content-Type": "application/json"
                    },
                    json=payload
                )

            if response.status_code == 200:
                task_id = response.json().get("id")
                logger.info("clickup_task_criada", task_id=task_id, lead_name=lead.name, score=lead.score)
                return task_id
            else:
                logger.error("clickup_task_falhou", status=response.status_code, body=response.text[:200])
                return None

        except Exception as e:
            logger.error("clickup_erro_inesperado", error=str(e))
            return None

    def _get_priority(self, score: int) -> int:
        """Converte score do lead em prioridade do ClickUp (1=urgente, 2=alta, 3=normal, 4=baixa)."""
        if score >= 80:
            return 1  # Urgente
        elif score >= 60:
            return 2  # Alta
        elif score >= 40:
            return 3  # Normal
        else:
            return 4  # Baixa

    def _build_task_description(self, lead: LeadSchema, briefing: str) -> str:
        """Monta a descrição formatada da tarefa com dados do lead."""
        area = lead.area_juridica or "Não identificada"
        score_label = "🔴 Quente" if lead.score >= 80 else ("🟡 Morno" if lead.score >= 50 else "🟢 Frio")

        return f"""## Dados do Lead

**Nome:** {lead.name}
**Canal:** Bot Breviliere (Telegram/WhatsApp)
**Área Jurídica:** {area}
**Score de Qualificação:** {lead.score}/100 {score_label}
**Consentimento LGPD:** {'Sim ✅' if lead.lgpd_consent else 'Não ❌'}

---

## Briefing de Triagem

{briefing}

---

*Gerado automaticamente pelo Bot Breviliere*
"""
