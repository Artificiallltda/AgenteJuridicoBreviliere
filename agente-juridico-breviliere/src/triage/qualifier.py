def calculate_lead_score(triage_answers: list) -> int:
    """Calcula o score de qualificacao do lead (0-100).

    Criterios:
    - Respondeu >= 4 perguntas gerais: +40
    - Respondeu >= 8 perguntas (gerais + especificas): +30
    - Tem urgencia declarada: +20
    - Possui documentos: +10
    """
    score = 0

    if len(triage_answers) >= 4:
        score += 40

    if len(triage_answers) >= 8:
        score += 30

    # Verifica se declarou urgencia
    answers_text = " ".join(str(v).lower() for v in triage_answers if isinstance(v, dict))
    if "urgente" in answers_text or "urgencia" in answers_text or "prazo" in answers_text:
        score += 20

    # Verifica se possui documentos
    if "sim" in answers_text and ("documento" in answers_text or "ctps" in answers_text):
        score += 10

    return min(score, 100)
