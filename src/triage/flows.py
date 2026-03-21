from triage.questions import TRIAGE_QUESTIONS
from models.conversation import ConversationState
from typing import Optional

class TriageFlow:
    @staticmethod
    def get_eligible_questions(state: ConversationState) -> list:
        """Filtra perguntas que atendem as condicoes baseado nas respostas atuais."""
        area = state.area_juridica or "geral"
        all_questions = list(TRIAGE_QUESTIONS["geral"])
        
        # Adiciona perguntas especificas da area se existir
        if area and area in TRIAGE_QUESTIONS:
            all_questions.extend(TRIAGE_QUESTIONS[area])

        answered_map = {ans["id"]: ans["resposta"] for ans in state.triage_answers}
        eligible = []

        for q in all_questions:
            cond = q.get("condicional")
            if cond:
                target_id = cond["campo"]
                expected_val = cond["valor"].lower()
                actual_val = str(answered_map.get(target_id, "")).lower()

                if expected_val not in actual_val:
                    continue  # Pula pergunta se condicao nao atendida

            eligible.append(q)

        return eligible

    @staticmethod
    def get_next_question(state: ConversationState) -> Optional[str]:
        """Retorna a proxima pergunta elegivel baseada na logica adaptativa."""
        eligible_questions = TriageFlow.get_eligible_questions(state)
        answered_ids = {ans["id"] for ans in state.triage_answers}

        for q in eligible_questions:
            if q["id"] not in answered_ids:
                return q["pergunta"]
        
        # Todas perguntas elegiveis foram respondidas
        return None

    @staticmethod
    def get_progress(state: ConversationState) -> dict:
        """Calcula o progresso atual considerando apenas perguntas elegiveis."""
        eligible = TriageFlow.get_eligible_questions(state)
        answered_ids = {ans["id"] for ans in state.triage_answers}

        # Filtra elegiveis que realmente estao na lista de perguntas
        total = len(eligible)
        respondidas = sum(1 for q in eligible if q["id"] in answered_ids)

        percentual = int((respondidas / total * 100)) if total > 0 else 100

        return {
            "total": total,
            "respondidas": respondidas,
            "percentual": percentual
        }
