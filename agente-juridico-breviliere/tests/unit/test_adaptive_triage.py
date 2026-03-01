import pytest
from src.triage.flows import TriageFlow
from src.triage.qualifier import calculate_lead_score
from src.triage.questions import TRIAGE_QUESTIONS
from src.models.conversation import ConversationState, ChannelType

@pytest.fixture
def state():
    return ConversationState(
        session_id="test_adaptive",
        channel=ChannelType.WHATSAPP,
        current_step="triage"
    )

def test_conditional_question_appears_when_met(state):
    # 'tem_documento' -> 'sim' deve mostrar 'tipo_documento'
    state.triage_answers = [
        {"id": "nome", "resposta": "Joao"},
        {"id": "cidade_estado", "resposta": "SP"},
        {"id": "motivo", "resposta": "ajuda"},
        {"id": "urgencia", "resposta": "nao"},
        {"id": "tem_documento", "resposta": "sim"}
    ]
    next_q = TriageFlow.get_next_question(state)
    assert next_q == "Quais documentos voce possui?"

def test_conditional_question_skipped_when_not_met(state):
    # 'tem_documento' -> 'nao' deve PULAR 'tipo_documento' e ir para area especifica (se houver)
    state.triage_answers = [
        {"id": "nome", "resposta": "Joao"},
        {"id": "cidade_estado", "resposta": "SP"},
        {"id": "motivo", "resposta": "ajuda"},
        {"id": "urgencia", "resposta": "nao"},
        {"id": "tem_documento", "resposta": "nao"}
    ]
    state.area_juridica = "trabalhista"
    next_q = TriageFlow.get_next_question(state)
    # Proxima deve ser a primeira de trabalhista
    assert next_q == TRIAGE_QUESTIONS["trabalhista"][0]["pergunta"]

def test_score_uses_weights():
    # Pergunta 'motivo' tem peso 10, 'nome' tem peso 5
    answers = [
        {"id": "nome", "resposta": "Joao"}, # 5
        {"id": "motivo", "resposta": "demissao"} # 10
    ]
    score = calculate_lead_score(answers)
    # (15 / 80) * 100 = 18.75 -> 18
    assert score == 18

def test_get_progress_returns_correct_values(state):
    state.triage_answers = [{"id": "nome", "resposta": "Joao"}]
    progress = TriageFlow.get_progress(state)
    assert progress["respondidas"] == 1
    assert progress["total"] > 1
    assert progress["percentual"] > 0

def test_criminal_area_questions_exist():
    assert "criminal" in TRIAGE_QUESTIONS
    assert len(TRIAGE_QUESTIONS["criminal"]) >= 3
    assert TRIAGE_QUESTIONS["criminal"][0]["id"] == "situacao_liberdade"

def test_previdenciario_area_questions_exist():
    assert "previdenciario" in TRIAGE_QUESTIONS
    assert len(TRIAGE_QUESTIONS["previdenciario"]) >= 3
    assert TRIAGE_QUESTIONS["previdenciario"][2]["condicional"]["campo"] == "ja_requereu"
