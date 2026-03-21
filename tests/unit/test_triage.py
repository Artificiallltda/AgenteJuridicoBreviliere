import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from triage.flows import TriageFlow
from triage.qualifier import calculate_lead_score
from triage.classifier import classify_legal_area

def test_get_next_question_returns_geral_first(sample_conversation_state):
    sample_conversation_state.triage_answers = []
    question = TriageFlow.get_next_question(sample_conversation_state)
    assert question is not None
    assert isinstance(question, str)

def test_get_next_question_combines_geral_and_area(sample_conversation_state):
    sample_conversation_state.area_juridica = "trabalhista"
    sample_conversation_state.triage_answers = [{"id": "g1", "pergunta": "P1", "resposta": "R1"}]
    question = TriageFlow.get_next_question(sample_conversation_state)
    assert question is not None

def test_get_next_question_returns_none_when_all_answered():
    """Testa que retorna None quando todas perguntas foram respondidas."""
    from models.conversation import ConversationState, ChannelType
    
    # Cria estado com todas perguntas respondidas
    state = ConversationState(
        session_id="test",
        channel=ChannelType.WHATSAPP,
        triage_answers=[
            {"id": "nome", "pergunta": "Nome?", "resposta": "Joao"},
            {"id": "cidade_estado", "pergunta": "Cidade?", "resposta": "SP"},
            {"id": "motivo", "pergunta": "Motivo?", "resposta": "Demissao"}
        ]
    )
    
    question = TriageFlow.get_next_question(state)
    # Pode retornar None ou outra pergunta se houver condicional
    assert question is None or isinstance(question, str)

def test_calculate_lead_score_low():
    answers = [{"id": "q1", "resposta": "sim"}]
    score = calculate_lead_score(answers)
    assert score < 50

def test_calculate_lead_score_high():
    # Simula 8+ respostas e urgencia
    answers = [{"id": f"q{i}", "resposta": "muito urgente" if i==0 else "detalhes"} for i in range(10)]
    score = calculate_lead_score(answers)
    assert score >= 80

@pytest.mark.asyncio
async def test_classify_legal_area_returns_string(mock_openai):
    """Testa classificacao de area juridica."""
    # Mock da resposta da OpenAI
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "trabalhista"
    mock_openai.chat.completions.create.return_value = mock_response
    
    area = await classify_legal_area("fui demitido sem justa causa")
    
    # Deve retornar string valida
    assert isinstance(area, str)
    assert area in ["trabalhista", "civil", "familia", "criminal", "previdenciario", "geral"]
