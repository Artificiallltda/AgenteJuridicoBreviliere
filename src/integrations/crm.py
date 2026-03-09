import httpx
from src.models.lead import LeadSchema
from src.config.settings import get_settings
from src.config.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class CRMIntegration:
    """Integra com CRM (Pipedrive/HubSpot) para envio de leads qualificados."""

    def __init__(self):
        self.base_url = settings.crm_api_url
        self.api_token = settings.crm_api_token

    async def create_lead(self, lead: LeadSchema) -> str:
        """Cria um novo lead/person no CRM.

        Returns:
            ID do lead criado ou None em caso de erro.
        """
        url = f"{self.base_url}/persons"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {
            "name": lead.name,
            "phone": [{"value": lead.phone, "primary": True}],
            "email": [{"value": lead.email, "primary": True}] if lead.email else [],
            "custom_fields": {
                "area_juridica": lead.area_juridica,
                "score": lead.score,
                "urgencia": lead.urgency or "N/A"
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code == 201:
                    lead_id = response.json().get("data", {}).get("id")
                    logger.info("lead_criado_crm", lead_id=lead_id, name=lead.name)
                    return lead_id
                else:
                    logger.error("erro_criar_lead_crm", status=response.status_code)
                    return None
        except Exception as e:
            logger.error("erro_conexao_crm", error=str(e))
            return None
