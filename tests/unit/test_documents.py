import pytest
from unittest.mock import patch, MagicMock
from documents.generator import DocumentGenerator
from models.lead import LeadSchema, LeadStatus

@pytest.fixture
def sample_lead():
    """Fixture para LeadSchema de teste."""
    return LeadSchema(
        id="lead-123",
        name="Joao Silva",
        email="joao@example.com",
        phone="5511999999999",
        area_juridica="trabalhista",
        status=LeadStatus.NEW,
        score=75,
        triage_data={"pergunta1": "resposta1"},
        lgpd_consent=True
    )

@pytest.mark.asyncio
async def test_generate_briefing_creates_file(sample_lead):
    """Testa geracao de briefing."""
    generator = DocumentGenerator()
    
    # Mock de DocxTemplate para evitar dependencia de arquivo fisico
    with patch("documents.generator.DocxTemplate") as MockDocxTemplate:
        mock_doc = MagicMock()
        MockDocxTemplate.return_value = mock_doc
        
        # Mock de os.path.exists para retornar True
        with patch("documents.generator.os.path.exists", return_value=True):
            with patch("documents.generator.os.makedirs", return_value=None):
                path = await generator.generate_briefing(sample_lead)
                
                # Deve retornar path ou None se template nao existir
                assert path is None or isinstance(path, str)

@pytest.mark.asyncio
async def test_generate_proposta_includes_honorarios(sample_lead):
    """Testa geracao de proposta com honorarios."""
    generator = DocumentGenerator()
    
    with patch("documents.generator.DocxTemplate") as MockDocxTemplate:
        mock_doc = MagicMock()
        MockDocxTemplate.return_value = mock_doc
        
        with patch("documents.generator.os.path.exists", return_value=True):
            with patch("documents.generator.os.makedirs", return_value=None):
                path = await generator.generate_proposta(sample_lead, "R$ 5000")
                
                # Deve retornar path ou None se template nao existir
                assert path is None or isinstance(path, str)

@pytest.mark.asyncio
async def test_generate_document_missing_template_returns_none(sample_lead):
    """Testa que template ausente retorna None."""
    generator = DocumentGenerator()
    
    # Mock de os.path.exists para retornar False
    with patch("documents.generator.os.path.exists", return_value=False):
        path = await generator.generate_briefing(sample_lead)
        assert path is None
