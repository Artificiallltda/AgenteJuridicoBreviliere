from src.models.conversation import ConversationState

def _user_consented(msg: str) -> bool:
    """Verifica se a mensagem do usuário representa consentimento LGPD."""
    clean = msg.lower().strip()
    if not clean:
        return False
        
    exact_matches = ["s", "ok", "okay", "yep", "yes", "tudo bem", "pode", "positivo"]
    if clean in exact_matches:
        return True
        
    if clean.startswith("ac"):
        return True
        
    contains_matches = ["sim", "concordo", "claro", "pode ser", "tá bom", "ta bom"]
    return any(phrase in clean for phrase in contains_matches)
from src.core.llm import LLMClient
from src.core.prompts import (
    SYSTEM_PROMPT,
    TRIAGE_PROMPT,
    RAG_PROMPT,
    CONSENT_PROMPT,
    HANDOFF_PROMPT
)
from src.triage.flows import TriageFlow
from src.triage.classifier import classify_legal_area
from src.triage.qualifier import calculate_lead_score
from src.handoff.manager import HandoffManager
from src.rag.indexer import LegalIndexer
from src.config.logging import get_logger

logger = get_logger(__name__)
llm = LLMClient()
handoff_manager = HandoffManager()
indexer = LegalIndexer()

async def process_message(state: ConversationState, user_message: str) -> str:
    """
    Processa a mensagem do usuario e gerencia o estado da conversacao.
    Retorna a resposta a ser enviada ao usuario.
    """
    logger.info("processando_mensagem", session_id=state.session_id, step=state.current_step)

    # Atualiza historico com mensagem do usuario
    state.history.append({"role": "user", "content": user_message})

    response = ""

    # 1. Verificacao de Consentimento LGPD
    if not state.lgpd_consent:
        if _user_consented(user_message):
            state.lgpd_consent = True
            state.current_step = "triage"
            next_q = TriageFlow.get_next_question(state)
            response = f"Ótimo! Para começar, preciso de algumas informações. 😊\n\n{next_q}" if next_q else "Obrigado pelo consentimento!"
        else:
            response = CONSENT_PROMPT

    # 2. Fluxo de Triagem
    elif state.current_step == "triage":
        # Recupera qual era a ultima pergunta feita para registrar corretamente
        all_questions = _get_all_questions(state)
        answered_count = len(state.triage_answers)

        if answered_count < len(all_questions):
            current_q = all_questions[answered_count]
            state.triage_answers.append({
                "id": current_q["id"],
                "pergunta": current_q["pergunta"],
                "resposta": user_message
            })

        # Classifica area juridica apos a pergunta de motivo
        if len(state.triage_answers) >= 3 and not state.area_juridica:
            motivo = next(
                (a["resposta"] for a in state.triage_answers if a["id"] == "motivo"),
                user_message
            )
            state.area_juridica = await classify_legal_area(motivo)
            logger.info("area_classificada", area=state.area_juridica, session_id=state.session_id)

        next_q = TriageFlow.get_next_question(state)
        progress = TriageFlow.get_progress(state)

        if next_q:
            # Usa o LLM para tornar a pergunta mais natural e empatica
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{TRIAGE_PROMPT.format(
                    area=state.area_juridica or 'Geral',
                    pergunta_atual=next_q,
                    respostas_anteriores=str(state.triage_answers)
                )}\n\nProgresso: {progress['respondidas']}/{progress['total']} perguntas"}
            ]
            response = await llm.get_response(messages)
        else:
            # Fim da triagem: calcular score e ir para briefing
            state.score = calculate_lead_score(state.triage_answers)
            state.current_step = "briefing"
            logger.info("triagem_concluida", score=state.score, area=state.area_juridica, session_id=state.session_id)
            response = "Perfeito. Já anotei tudo o que precisamos. Deixe-me preparar um resumo para nossa equipe de advogados. Um momento... ⏳"

    # 3. Fluxo de Briefing
    elif state.current_step == "briefing":
        # Resumo interno gerado — não exibe dados brutos ao cliente
        state.current_step = "handoff"
        response = "Ótimo! Já tenho todas as informações necessárias. Vou encaminhar agora para um dos nossos advogados especialistas. 📋"

    # 4. Fluxo de Handoff
    elif state.current_step == "handoff":
        briefing_lines = [f"Q: {a['pergunta']} | R: {a['resposta']}" for a in state.triage_answers]
        briefing_text = "\n".join(briefing_lines)
        await handoff_manager.request_handoff(
            state=state,
            briefing=f"Briefing do Cliente (score: {state.score}):\n{briefing_text}"
        )
        response = HANDOFF_PROMPT
        state.current_step = "closed"

    # 5. Fluxo RAG (consulta a base de conhecimento)
    elif state.current_step == "rag":
        search_results = await indexer.query(user_message, n_results=2)
        docs = search_results.get("documents", [[]])
        context = "\n".join(docs[0]) if docs and docs[0] else "Nenhuma informacao encontrada."

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": RAG_PROMPT.format(
                contexto=context,
                pergunta=user_message
            )}
        ]
        response = await llm.get_response(messages)

    # 6. Conversa encerrada
    elif state.current_step == "closed":
        response = "Seu atendimento já foi encaminhado para nossa equipe. Um advogado especialista entrará em contato em breve. Se precisar de algo, estarei aqui. 😊"

    # Fallback
    else:
        response = "Desculpe, não entendi bem. Como posso te ajudar hoje?"

    state.history.append({"role": "assistant", "content": response})
    return response


def _get_all_questions(state: ConversationState) -> list:
    """Retorna a lista completa de perguntas (gerais + area especifica)."""
    from src.triage.questions import TRIAGE_QUESTIONS

    area = state.area_juridica or "geral"
    questions = list(TRIAGE_QUESTIONS["geral"])
    if area != "geral" and area in TRIAGE_QUESTIONS:
        questions.extend(TRIAGE_QUESTIONS[area])
    return questions
