"""
DEPRECATED: Este arquivo contém uma implementação de referência do grafo LangGraph.

A implementação ativa está em conversation.py usando fluxo imperativo.

PARA FUTURA MIGRAÇÃO:
- Substituir process_message() em conversation.py para usar este grafo
- Ou integrar o grafo como backend do process_message

Status: Código mantido como referência, mas não utilizado em produção.
"""

from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import StateGraph, END
from models.conversation import ConversationState
from triage.classifier import classify_legal_area
from triage.qualifier import calculate_lead_score
from rag.indexer import LegalIndexer
from config.logging import get_logger

logger = get_logger(__name__)

# Singleton do LegalIndexer (evita recriar ChromaDB client a cada chamada)
_legal_indexer = None

def _get_indexer():
    global _legal_indexer
    if _legal_indexer is None:
        _legal_indexer = LegalIndexer()
    return _legal_indexer

# Definindo o Estado do Agente
class AgentState(TypedDict):
    conversation: ConversationState
    last_user_message: str
    next_node: str

# Nós do Grafo
async def node_check_consent(state: AgentState):
    """Verifica consentimento LGPD."""
    if state["conversation"].lgpd_consent:
        return {"next_node": "identify_client"}
    return {"next_node": "request_consent"}

async def node_identify_client(state: AgentState):
    """Identifica se o cliente já existe ou é um novo lead."""
    logger.info("identificando_cliente", session_id=state["conversation"].session_id)
    return {"next_node": "classify_intent"}

async def node_triage(state: AgentState):
    """Fluxo de Triagem Adaptativa."""
    logger.info("executando_triagem", session_id=state["conversation"].session_id)
    return {"next_node": "respond"}

async def node_rag_answer(state: AgentState):
    """Busca respostas na base juridica do escritorio via RAG."""
    indexer = _get_indexer()
    results = await indexer.query(state["last_user_message"])
    logger.info("rag_consulta_realizada", results_count=len(results['ids']))
    return {"next_node": "respond"}

async def node_generate_briefing(state: AgentState):
    """Gera o briefing juridico e, para leads quentes, a proposta de honorarios."""
    from documents.generator import DocumentGenerator
    from models.lead import LeadSchema

    generator = DocumentGenerator()
    conv = state["conversation"]

    # Converter ConversationState para LeadSchema (que o DocumentGenerator espera)
    lead = LeadSchema(
        id=conv.session_id,
        name=conv.triage_answers[0].get("resposta", "N/A") if conv.triage_answers else "N/A",
        phone="",
        area_juridica=conv.area_juridica,
        score=conv.score,
        triage_data={"answers": conv.triage_answers},
    )

    # 1. Gera o briefing estruturado para a equipe
    briefing_path = await generator.generate_briefing(lead)
    logger.info("briefing_gerado", session_id=conv.session_id, path=briefing_path)

    # 2. Se o lead for qualificado (score >= 80), gera a proposta automaticamente
    if lead.score >= 80:
        proposta_path = await generator.generate_proposta(lead)
        logger.info("proposta_automatica_gerada", session_id=conv.session_id, path=proposta_path)

    return {"next_node": "handoff"}

async def node_handoff(state: AgentState):
    """Prepara a transferência para atendimento humano."""
    logger.info("solicitando_handoff_humano", session_id=state["conversation"].session_id)
    return {"next_node": "respond"}

async def node_respond(state: AgentState):
    """Nó final de resposta ao usuário."""
    logger.info("preparando_resposta_final")
    return {"next_node": END}

# Edges Condicionais
# Palavras-chave que indicam que o usuário quer iniciar triagem (tem um caso)
_TRIAGE_KEYWORDS = [
    "demitido", "demissão", "processo", "divorcio", "divórcio",
    "acidente", "dívida", "dívidas", "cobrança", "inss", "aposentadoria",
    "fui preso", "preso", "guarda", "pensão", "inventário",
    "fui", "preciso de ajuda", "preciso contratar", "quero contratar",
    "meu caso", "meu direito", "me ajuda", "ajuda jurídica",
    "não recebi", "não pagou", "me debi", "rescisão"
]

def route_intent(state: AgentState):
    """Roteia para Triagem ou RAG baseado em palavras-chave de intenção."""
    msg = state["last_user_message"].lower()
    if any(k in msg for k in _TRIAGE_KEYWORDS):
        return "triage"
    return "rag_answer"

def build_agent_graph() -> StateGraph:
    """Constrói a máquina de estados completa do Agente Jurídico Breviliere."""
    
    workflow = StateGraph(AgentState)

    # Adicionar Nós
    workflow.add_node("check_consent", node_check_consent)
    workflow.add_node("identify_client", node_identify_client)
    workflow.add_node("triage", node_triage)
    workflow.add_node("rag_answer", node_rag_answer)
    workflow.add_node("generate_briefing", node_generate_briefing)
    workflow.add_node("handoff", node_handoff)
    workflow.add_node("respond", node_respond)

    # Definir Edges
    workflow.set_entry_point("check_consent")
    
    # Transições simples
    workflow.add_edge("identify_client", "triage") 
    workflow.add_edge("triage", "generate_briefing")
    workflow.add_edge("generate_briefing", "handoff")
    workflow.add_edge("handoff", "respond")
    workflow.add_edge("rag_answer", "respond")
    workflow.add_edge("respond", END)

    return workflow.compile()
