"""
Classificador de Intenção via IA.

Usa o GPT-4o-mini para identificar a intenção do usuário no atendimento.
Substitui a lógica frágil baseada no tamanho da mensagem.
"""

from typing import Literal
from core.llm import LLMClient
from config.logging import get_logger

logger = get_logger(__name__)

# Prompt padrão para classificação
_CLASSIFY_PROMPT = """
Você é um classificador de intenções para um bot de atendimento jurídico (Breviliere).
Analise a última mensagem do usuário e classifique em UMA das opções:

- "triage": O usuário está explicando o caso dele, quer processar alguém, quer se divorciar, etc.
- "rag": O usuário está apenas fazendo uma pergunta jurídica geral (ex: "o que é usucapião?").
- "greeting": Apenas saudações (ex: "oi", "bom dia", "tudo bem").
- "other": Reclamações, agradecimentos finais ou mensagens irrelevantes.

Responda APENAS com a palavra da classificação ("triage", "rag", "greeting" ou "other").
"""

async def classify_intent(message: str) -> Literal["triage", "rag", "greeting", "other"]:
    """
    Identifica a intenção do usuário chamando o LLM.
    """
    try:
        # Pega uma instância do LLM (usando modelo mais rápido/barato)
        llm = LLMClient()
        
        messages = [
            {"role": "system", "content": _CLASSIFY_PROMPT},
            {"role": "user", "content": f"Mensagem do usuário: '{message}'"}
        ]
        
        # Override para o gpt-4o-mini já configurado no settings
        response = await llm.get_response(messages)
        classification = response.lower().strip()
        
        # Fallback e validação de segurança
        accepted = ["triage", "rag", "greeting", "other"]
        if classification not in accepted:
            logger.warning("classificacao_invalida", result=classification)
            # Na dúvida, iniciamos a triagem se passar de 3 palavras, senão assumimos saudação
            return "triage" if len(message.split()) > 3 else "greeting"
            
        return classification # type: ignore
        
    except Exception as e:
        logger.error("erro_classificador_intent", error=str(e))
        # Fallback conservador
        return "triage" 
