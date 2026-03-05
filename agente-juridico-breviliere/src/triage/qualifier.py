from src.triage.questions import TRIAGE_QUESTIONS

def calculate_lead_score(triage_answers: list, area: str = "geral") -> int:
    """
    Calcula o score de qualificação do lead (0-100) baseado em pesos.
    Usa denominador dinâmico baseado nas perguntas reais da área jurídica.
    """
    score = 0

    # Mapeia todas as perguntas para fácil consulta de peso
    all_q_map = {}
    for area_key in TRIAGE_QUESTIONS:
        for q in TRIAGE_QUESTIONS[area_key]:
            all_q_map[q["id"]] = q.get("peso", 5)

    # Soma pesos das perguntas respondidas
    for ans in triage_answers:
        q_id = ans.get("id")
        score += all_q_map.get(q_id, 5)

    # Denominador dinâmico: soma dos pesos das perguntas elegivíeis para a área
    eligible_questions = list(TRIAGE_QUESTIONS.get("geral", []))
    if area != "geral" and area in TRIAGE_QUESTIONS:
        eligible_questions += TRIAGE_QUESTIONS[area]
    max_theoretical = sum(q.get("peso", 5) for q in eligible_questions) or 80

    # Bônus de Urgência
    answers_text = " ".join(str(v.get("resposta", "")).lower() for v in triage_answers)
    if any(word in answers_text for word in ["urgente", "urgencia", "urgência", "prazo", "vencendo", "audiencia", "audiência"]):
        score += 15

    # Bônus de Documentos
    if "sim" in answers_text and "documento" in answers_text:
        score += 10

    # Normalização 0-100
    final_score = int((score / max_theoretical) * 100)
    return min(final_score, 100)
