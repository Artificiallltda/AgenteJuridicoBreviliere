TRIAGE_QUESTIONS = {
    "geral": [
        {"id": "nome", "pergunta": "Qual seu nome completo?", "tipo": "text", "peso": 5},
        {"id": "cidade_estado", "pergunta": "Em qual cidade e estado voce esta?", "tipo": "text", "peso": 3},
        {"id": "motivo", "pergunta": "Me conte brevemente o que esta acontecendo. Qual o motivo do seu contato?", "tipo": "text", "peso": 10},
        {"id": "urgencia", "pergunta": "Existe alguma urgencia? (prazo vencendo, audiencia marcada, etc.)", "tipo": "yesno", "peso": 10},
        {"id": "tem_documento", "pergunta": "Voce possui documentos relacionados ao caso?", "tipo": "yesno", "peso": 5},
        {"id": "tipo_documento", "pergunta": "Quais documentos voce possui?", "tipo": "text", "peso": 3, "condicional": {"campo": "tem_documento", "valor": "sim"}},
    ],
    "trabalhista": [
        {"id": "vinculo", "pergunta": "Qual o tipo de vinculo? (CLT, PJ, temporario)", "tipo": "choice", "peso": 8},
        {"id": "tempo_empresa", "pergunta": "Ha quanto tempo trabalha/trabalhou na empresa?", "tipo": "text", "peso": 5},
        {"id": "verbas", "pergunta": "Recebeu todas as verbas rescisoriarias corretamente?", "tipo": "yesno", "peso": 10},
        {"id": "fgts", "pergunta": "O FGTS foi depositado corretamente?", "tipo": "yesno", "peso": 7},
    ],
    "civil": [
        {"id": "tipo_civil", "pergunta": "Trata-se de: contrato, divida, danos, consumidor ou outro?", "tipo": "choice", "peso": 7},
        {"id": "contraparte", "pergunta": "Quem e a outra parte envolvida?", "tipo": "text", "peso": 5},
        {"id": "valor_causa", "pergunta": "Qual o valor aproximado envolvido na disputa?", "tipo": "text", "peso": 8},
    ],
    "familia": [
        {"id": "tipo_familia", "pergunta": "Trata-se de: divorcio, pensao, guarda, inventario ou outro?", "tipo": "choice", "peso": 9},
        {"id": "filhos", "pergunta": "Ha filhos menores envolvidos?", "tipo": "yesno", "peso": 10},
        {"id": "consenso", "pergunta": "Ha consenso entre as partes?", "tipo": "yesno", "peso": 8},
    ],
    "criminal": [
        {"id": "situacao_liberdade", "pergunta": "A pessoa envolvida esta em liberdade ou presa?", "tipo": "choice", "peso": 10},
        {"id": "tem_processo", "pergunta": "Ja existe um processo criminal em andamento?", "tipo": "yesno", "peso": 8},
        {"id": "fase_processo", "pergunta": "Em qual fase esta o processo? (inquerito, denuncia, julgamento)", "tipo": "text", "peso": 7, "condicional": {"campo": "tem_processo", "valor": "sim"}},
    ],
    "previdenciario": [
        {"id": "tipo_beneficio", "pergunta": "Qual beneficio voce busca? (aposentadoria, auxilio-doenca, BPC, etc.)", "tipo": "choice", "peso": 9},
        {"id": "ja_requereu", "pergunta": "Ja fez o requerimento no INSS?", "tipo": "yesno", "peso": 7},
        {"id": "tem_negativa", "pergunta": "Houve negativa do INSS?", "tipo": "yesno", "peso": 10, "condicional": {"campo": "ja_requereu", "valor": "sim"}},
    ]
}
