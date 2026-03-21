import os
from datetime import datetime, UTC
from docxtpl import DocxTemplate
from models.lead import LeadSchema
from config.settings import get_settings
from config.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

class DocumentGenerator:
    def __init__(self):
        self.templates_path = "src/documents/templates"
        self.output_path = "data/outputs"
        os.makedirs(self.output_path, exist_ok=True)

    def _get_common_context(self, lead: LeadSchema) -> dict:
        """Retorna o contexto comum para todos os documentos."""
        return {
            "name": lead.name,
            "phone": lead.phone,
            "email": lead.email or "N/A",
            "area": lead.area_juridica or "Geral",
            "score": lead.score,
            "date": datetime.now(UTC).strftime("%d/%m/%Y"),
            "year": datetime.now(UTC).year,
            "answers": lead.triage_data
        }

    async def _generate_document(self, lead: LeadSchema, doc_type: str, extra_context: dict = None) -> str:
        """Método genérico para geração de documentos via templates DOCX."""
        template_file = os.path.join(self.templates_path, f"{doc_type}.docx")
        
        if not os.path.exists(template_file):
            logger.error("template_nao_encontrado", doc_type=doc_type, path=template_file)
            return None
            
        try:
            doc = DocxTemplate(template_file)
            context = self._get_common_context(lead)
            if extra_context:
                context.update(extra_context)
            
            doc.render(context)
            
            file_name = f"{doc_type}_{lead.id}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.docx"
            target_path = os.path.join(self.output_path, file_name)
            doc.save(target_path)
            
            logger.info("documento_gerado_com_sucesso", doc_type=doc_type, path=target_path)
            return target_path
        except Exception as e:
            logger.error("erro_geracao_documento", doc_type=doc_type, error=str(e))
            return None

    async def generate_briefing(self, lead: LeadSchema) -> str:
        """Gera o briefing jurídico estruturado para a equipe interna."""
        return await self._generate_document(lead, "briefing")

    async def generate_proposta(self, lead: LeadSchema, honorarios: str = "A definir") -> str:
        """Gera a proposta de honorários para o cliente."""
        extra = {"honorarios": honorarios}
        return await self._generate_document(lead, "proposta", extra)

    async def generate_contrato(self, lead: LeadSchema) -> str:
        """Gera o contrato de prestação de serviços jurídicos."""
        return await self._generate_document(lead, "contrato")
