from src.triage.questions import TRIAGE_QUESTIONS
from src.models.conversation import ConversationState

class TriageFlow:
    @staticmethod
    def get_eligible_questions(state: ConversationState) -> list:
        """Filtra perguntas que atendem as condicoes baseado nas respostas atuais."""
        area = state.area_juridica or "geral"
        all_questions = TRIAGE_QUESTIONS["geral"] + TRIAGE_QUESTIONS.get(area, [])
        
        answered_map = {ans["id"]: ans["resposta"] for ans in state.triage_answers}
        eligible = []
        
        for q in all_questions:
            cond = q.get("condicional")
            if cond:
                target_id = cond["campo"]
                expected_val = cond["valor"].lower()
                actual_val = str(answered_map.get(target_id, "")).lower()
                
                if expected_val not in actual_val:
                    continue # Pula pergunta se condicao nao atendida
            
            eligible.append(q)
            
        return eligible

    @staticmethod
    def get_next_question(state: ConversationState) -> str:
        """Retorna a proxima pergunta elegivel baseada na logica adaptativa."""
        eligible_questions = TriageFlow.get_eligible_questions(state)
        answered_ids = [ans["id"] for ans in state.triage_answers]
        
        for q in eligible_questions:
            if q["id"] not in answered_ids:
                return q["pergunta"]
        return None

    @staticmethod
    def get_progress(state: ConversationState) -> dict:
        """Calcula o progresso atual considerando apenas perguntas elegiveis."""
        eligible = TriageFlow.get_eligible_questions(state)
        answered_ids = [ans["id"] for ans in state.triage_answers]
        
        # Filtra elegiveis que realmente estao na lista de perguntas (evita erros se mudarem perguntas no meio)
        total = len(eligible)
        respondidas = len([q for q in eligible if q["id"] in answered_ids])
        
        percentual = int((respondidas / total * 100)) if total > 0 else 100
        
        return {
            "total": total,
            "respondidas": respondidas,
            "percentual": percentual
        }
