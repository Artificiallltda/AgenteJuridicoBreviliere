from src.triage.questions import TRIAGE_QUESTIONS
from src.models.conversation import ConversationState

class TriageFlow:
    @staticmethod
    def get_next_question(state: ConversationState) -> str:
        """Combina perguntas gerais e especficas por rea."""
        area = state.area_juridica or "geral"
        # Combina geral + rea
        all_questions = TRIAGE_QUESTIONS["geral"] + TRIAGE_QUESTIONS.get(area, [])
        
        answered_ids = [ans["id"] for ans in state.triage_answers]
        
        for q in all_questions:
            if q["id"] not in answered_ids:
                return q["pergunta"]
        return None
