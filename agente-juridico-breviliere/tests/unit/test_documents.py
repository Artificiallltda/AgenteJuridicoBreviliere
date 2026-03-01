import pytest
import os
from unittest.mock import MagicMock, patch, AsyncMock
from src.documents.generator import DocumentGenerator

@pytest.fixture
def doc_gen():
    return DocumentGenerator()

@pytest.mark.asyncio
async def test_generate_briefing_creates_file(doc_gen, sample_lead):
    # Mock DocxTemplate e os.path.exists
    with patch("src.documents.generator.DocxTemplate") as mock_tpl, 
         patch("os.path.exists", return_value=True), 
         patch("os.makedirs"):
        
        mock_instance = mock_tpl.return_value
        path = await doc_gen.generate_briefing(sample_lead)
        
        assert path is not None
        assert "briefing_" in path
        assert mock_instance.save.called

@pytest.mark.asyncio
async def test_generate_proposta_includes_honorarios(doc_gen, sample_lead):
    with patch("src.documents.generator.DocxTemplate") as mock_tpl, 
         patch("os.path.exists", return_value=True), 
         patch("os.makedirs"):
        
        mock_instance = mock_tpl.return_value
        path = await doc_gen.generate_proposta(sample_lead, honorarios="R$ 5.000")
        
        assert path is not None
        # Verifica se render foi chamado com o contexto correto
        args, kwargs = mock_instance.render.call_args
        assert args[0]["honorarios"] == "R$ 5.000"

@pytest.mark.asyncio
async def test_generate_document_missing_template_returns_none(doc_gen, sample_lead):
    with patch("os.path.exists", return_value=False):
        path = await doc_gen._generate_document(sample_lead, "template_fantasma")
        assert path is None
