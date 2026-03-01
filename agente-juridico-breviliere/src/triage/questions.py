TRIAGE_QUESTIONS = {
    "geral": [
        {"id": "nome", "pergunta": "Qual seu nome completo?", "obrigatoria": True},
        {"id": "cidade_estado", "pergunta": "Em qual cidade e estado você está?", "obrigatoria": True},
        {"id": "motivo", "pergunta": "Me conte brevemente o que está acontecendo. Qual o motivo do seu contato?", "obrigatoria": True},
        {"id": "urgencia", "pergunta": "Existe alguma urgência? (prazo vencendo, audiência marcada, etc.)", "obrigatoria": True},
    ],
    "trabalhista": [
        {"id": "vinculo", "pergunta": "Qual o tipo de vínculo? (CLT, PJ, temporário)", "obrigatoria": True},
        {"id": "tempo_empresa", "pergunta": "Há quanto tempo trabalha/trabalhou na empresa?", "obrigatoria": True},
        {"id": "verbas", "pergunta": "Recebeu todas as verbas rescisórias corretamente?", "obrigatoria": True},
    ],
    "civil": [
        {"id": "tipo_civil", "pergunta": "Trata-se de: contrato, dívida, danos, consumidor ou outro?", "obrigatoria": True},
        {"id": "contraparte", "pergunta": "Quem é a outra parte envolvida?", "obrigatoria": True},
    ],
    "familia": [
        {"id": "tipo_familia", "pergunta": "Trata-se de: divórcio, pensão, guarda, inventário ou outro?", "obrigatoria": True},
        {"id": "filhos", "pergunta": "Há filhos menores envolvidos?", "obrigatoria": True},
    ],
}
