from models.conversation import ConversationState

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
from core.llm import LLMClient
from core.prompts import (
    SYSTEM_PROMPT,
    TRIAGE_PROMPT,
    RAG_PROMPT,
    CONSENT_PROMPT,
    HANDOFF_PROMPT
)
from triage.flows import TriageFlow
from triage.classifier import classify_legal_area
from triage.qualifier import calculate_lead_score
from handoff.manager import HandoffManager
from rag.indexer import LegalIndexer
from config.logging import get_logger

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

    responses = []

    # Loop de avanço automático de estados
    while True:
        # 1. Verificacao de Consentimento LGPD
        if not state.lgpd_consent:
            if _user_consented(user_message):
                state.lgpd_consent = True
                state.current_step = "triage"
                # Após consentimento, avança para triagem imediatamente (no próximo ciclo do while)
                responses.append("Ótimo! Para começar, preciso de algumas informações. 😊")
                continue
            else:
                responses.append(CONSENT_PROMPT)
                break

        # 2. Fluxo de Triagem
        if state.current_step == "triage":
            all_questions = _get_all_questions(state)
            answered_count = len(state.triage_answers)

            # Registra resposta se houver pergunta pendente
            if answered_count < len(all_questions):
                current_q = all_questions[answered_count]
                # Se a mensagem do usuário for apenas o consentimento (do passo anterior), não registra como resposta
                if user_message.lower().strip() not in ["sim", "concordo", "pode ser"]:
                    state.triage_answers.append({
                        "id": current_q["id"],
                        "pergunta": current_q["pergunta"],
                        "resposta": user_message
                    })

            # Classifica area juridica apos a pergunta de motivo
            if len(state.triage_answers) >= 3 and not state.area_juridica:
                motivo = next((a["resposta"] for a in state.triage_answers if a["id"] == "motivo"), user_message)
                state.area_juridica = await classify_legal_area(motivo)
                logger.info("area_classificada", area=state.area_juridica, session_id=state.session_id)

            next_q = TriageFlow.get_next_question(state)
            if next_q:
                progress = TriageFlow.get_progress(state)
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"{TRIAGE_PROMPT.format(
                        area=state.area_juridica or 'Geral',
                        pergunta_atual=next_q,
                        respostas_anteriores=str(state.triage_answers)
                    )}\n\nProgresso: {progress['respondidas']}/{progress['total']} perguntas"}
                ]
                q_text = await llm.get_response(messages)
                responses.append(q_text)
                break # Espera próxima resposta do usuário
            else:
                # Fim da triagem: calcular score e ir para briefing
                state.score = calculate_lead_score(state.triage_answers)
                state.current_step = "briefing"
                logger.info("triagem_concluida", score=state.score, area=state.area_juridica, session_id=state.session_id)
                responses.append("Perfeito. Já anotei tudo o que precisamos. Deixe-me preparar um resumo para nossa equipe de advogados. Um momento... ⏳")
                continue # Avança para briefing imediatamente

        # 3. Fluxo de Briefing (Automático)
        elif state.current_step == "briefing":
            state.current_step = "handoff"
            responses.append("Ótimo! Já tenho todas as informações necessárias. Vou encaminhar agora para um dos nossos advogados especialistas. 📋")
            continue # Avança para handoff imediatamente

        # 4. Fluxo de Handoff (Automático)
        elif state.current_step == "handoff":
            briefing_lines = [f"Q: {a['pergunta']} | R: {a['resposta']}" for a in state.triage_answers]
            briefing_text = "\n".join(briefing_lines)
            await handoff_manager.request_handoff(
                state=state,
                briefing=f"Briefing do Cliente (score: {state.score}):\n{briefing_text}"
            )
            responses.append(HANDOFF_PROMPT)
            state.current_step = "closed"
            continue # Avança para closed imediatamente

        # 5. Fluxo RAG (consulta a base de conhecimento)
        elif state.current_step == "rag":
            search_results = await indexer.query(user_message, n_results=2)
            docs = search_results.get("documents", [[]])
            context = "\n".join(docs[0]) if docs and docs[0] else "Nenhuma informacao encontrada."
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": RAG_PROMPT.format(contexto=context, pergunta=user_message)}
            ]
            r_text = await llm.get_response(messages)
            responses.append(r_text)
            break

        # 6. Conversa encerrada
        elif state.current_step == "closed":
            responses.append("Seu atendimento já foi encaminhado para nossa equipe. Um advogado especialista entrará em contato em breve. Se precisar de algo, estarei aqui. 😊")
            break

        # Fallback de segurança
        else:
            responses.append("Desculpe, não entendi bem. Como posso te ajudar hoje?")
            break

    final_response = "\n\n".join(responses)
    state.history.append({"role": "assistant", "content": final_response})
    return final_response



def _get_all_questions(state: ConversationState) -> list:
    """Retorna a lista completa de perguntas (gerais + area especifica)."""
    from triage.questions import TRIAGE_QUESTIONS

    area = state.area_juridica or "geral"
    questions = list(TRIAGE_QUESTIONS["geral"])
    if area != "geral" and area in TRIAGE_QUESTIONS:
        questions.extend(TRIAGE_QUESTIONS[area])
    return questions
