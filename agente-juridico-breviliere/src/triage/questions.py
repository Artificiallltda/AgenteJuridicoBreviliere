TRIAGE_QUESTIONS = {
    "geral": [
        {"id": "nome", "pergunta": "Qual seu nome completo?", "tipo": "text", "peso": 5},
        {"id": "cidade_estado", "pergunta": "Em qual cidade e estado voce esta?", "tipo": "text", "peso": 3},
        {"id": "motivo", "pergunta": "Me conte resumidamente o que esta acontecendo. Qual o principal motivo do contato?", "tipo": "text", "peso": 10},
    ],
    "trabalhista": [
        {"id": "vinculo", "pergunta": "Qual era o tipo de vinculo de trabalho? (CLT, PJ, temporario)", "tipo": "choice", "peso": 8},
        {"id": "rescisao", "pergunta": "O que aconteceu na saida? Chegou a receber as verbas e FGTS certinho?", "tipo": "text", "peso": 10},
    ],
    "civil": [
        {"id": "tipo_civil", "pergunta": "Essa disputa e sobre contrato, divida, danos, consumidor ou algo diferente?", "tipo": "choice", "peso": 7},
        {"id": "contraparte", "pergunta": "Quem esta do outro lado dessa disputa (outra pessoa, empresa, etc)?", "tipo": "text", "peso": 5},
    ],
    "familia": [
        {"id": "tipo_familia", "pergunta": "E um caso de divorcio, pensao, guarda, inventario ou outro?", "tipo": "choice", "peso": 9},
        {"id": "consenso", "pergunta": "As partes estao em acordo? E existem filhos menores?", "tipo": "text", "peso": 10},
    ],
    "criminal": [
        {"id": "situacao_liberdade", "pergunta": "A pessoa envolvida nisso esta presa ou em liberdade?", "tipo": "choice", "peso": 10},
    ],
    "previdenciario": [
        {"id": "tipo_beneficio", "pergunta": "Qual auxilio voce busca? (aposentadoria, auxilio-doenca, BPC, etc.)", "tipo": "choice", "peso": 9},
        {"id": "status_inss", "pergunta": "Ja chegou a abrir e receber resposta do pedido direto no INSS?", "tipo": "text", "peso": 10},
    ]
}
