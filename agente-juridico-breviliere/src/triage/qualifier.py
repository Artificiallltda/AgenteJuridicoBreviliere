from src.triage.questions import TRIAGE_QUESTIONS

def calculate_lead_score(triage_answers: list) -> int:
    """
    Calcula o score de qualificacao do lead (0-100) baseado em pesos.
    """
    score = 0
    max_score = 0
    
    # Mapeia todas as perguntas para facil consulta de peso
    all_q_map = {}
    for area in TRIAGE_QUESTIONS:
        for q in TRIAGE_QUESTIONS[area]:
            all_q_map[q["id"]] = q.get("peso", 5)

    # Soma pesos das perguntas respondidas
    for ans in triage_answers:
        q_id = ans.get("id")
        score += all_q_map.get(q_id, 5)

    # Max score teorico para normalizacao (aproximadamente 10 perguntas de peso 8)
    # Usaremos 80 como base de normalizacao para evitar scores muito baixos
    max_theoretical = 80

    # Bonus de Urgencia
    answers_text = " ".join(str(v.get("resposta", "")).lower() for v in triage_answers)
    if any(word in answers_text for word in ["urgente", "urgencia", "prazo", "vencendo", "audiencia"]):
        score += 15
        
    # Bonus de Documentos
    if "sim" in answers_text and "documento" in answers_text:
        score += 10

    # Normalizacao 0-100
    final_score = int((score / max_theoretical) * 100)
    return min(final_score, 100)
