import httpx
from src.integrations.crm import CRMIntegration
from src.config.logging import get_logger

logger = get_logger(__name__)

async def create_deal(crm: CRMIntegration, person_id: str, title: str, value: float = 0) -> str:
    """Cria um novo Negocio (Deal) no Pipedrive vinculado a uma pessoa."""
    url = f"{crm.base_url}/deals"
    headers = {"Authorization": f"Bearer {crm.api_token}"}
    payload = {
        "title": title,
        "person_id": person_id,
        "value": value,
        "currency": "BRL",
        "status": "open"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code in [200, 201]:
                deal_id = response.json().get("data", {}).get("id")
                logger.info("deal_criado_pipedrive", deal_id=deal_id, person_id=person_id)
                return str(deal_id)
            else:
                logger.error("erro_criar_deal_pipedrive", status=response.status_code, body=response.text)
                return None
    except Exception as e:
        logger.error("erro_conexao_pipedrive_deal", error=str(e))
        return None

async def add_note(crm: CRMIntegration, deal_id: str, content: str) -> bool:
    """Adiciona uma nota ao Negocio (Deal) no Pipedrive com o historico/briefing."""
    url = f"{crm.base_url}/notes"
    headers = {"Authorization": f"Bearer {crm.api_token}"}
    payload = {
        "deal_id": deal_id,
        "content": content
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code in [200, 201]:
                logger.info("nota_adicionada_pipedrive", deal_id=deal_id)
                return True
            else:
                logger.error("erro_adicionar_nota_pipedrive", status=response.status_code)
                return False
    except Exception as e:
        logger.error("erro_conexao_pipedrive_note", error=str(e))
        return False
