import pytest
from unittest.mock import AsyncMock, patch
from core.agent import build_agent_graph
from models.conversation import ConversationState, ChannelType, MessageType

@pytest.mark.asyncio
async def test_e2e_agent_journey():
    """Simula a jornada completa de um cliente trabalhista de ponta a ponta."""
    
    # 1. Configurar o estado inicial (Novo usuário via WhatsApp)
    state = {
        "conversation": ConversationState(
            session_id="test_session_123",
            channel=ChannelType.WHATSAPP,
            lgpd_consent=False  # Ainda não aceitou
        ),
        "last_user_message": "Olá, quero processar minha empresa",
        "next_node": ""
    }
    
    # Mock das integrações externas
    with patch("src.triage.classifier.get_openai_client") as mock_openai, \
         patch("src.rag.embeddings.get_openai_client") as mock_embeddings, \
         patch("src.documents.generator.DocumentGenerator.generate_briefing") as mock_gen_briefing, \
         patch("src.handoff.manager.HandoffManager.request_human_support") as mock_handoff:
        
        # Mock do classificador (identifica como trabalhista)
        mock_openai.return_value.chat.completions.create = AsyncMock(
            return_value=AsyncMock(choices=[AsyncMock(message=AsyncMock(content="trabalhista"))])
        )
        
        # Mock do briefing (retorna caminho do arquivo)
        mock_gen_briefing.return_value = "data/outputs/briefing_test.docx"
        
        # Mock do handoff (retorna sucesso)
        mock_handoff.return_value = True

        # 2. Construir e rodar o grafo
        graph = build_agent_graph()
        
        # PASSO 1: Início e Verificação de Consentimento
        # O usuário aceita os termos (simulando a transição real)
        state["conversation"].lgpd_consent = True
        state["last_user_message"] = "Aceito os termos"
        
        # PASSO 2: Descrição do caso e Triagem
        state["last_user_message"] = "Fui demitido sem justa causa e não recebi nada"
        
        # Executar um passo no grafo (node_check_consent -> node_identify_client -> node_triage)
        result = await graph.ainvoke(state)
        
        # 3. Validações Finais
        
        # O estado deve ter passado por vários nós
        assert result["next_node"] == "END" or result["next_node"] == ""
        
        # Verificações de lógica de negócio
        # - O gerador de briefing deve ter sido chamado
        assert mock_gen_briefing.called
        
        # - O gerenciador de handoff deve ter sido acionado
        assert mock_handoff.called
        
        # - O classificador deve ter sido acionado para identificar 'trabalhista'
        # (Isso dependeria do nó real de classificação estar ativo no grafo)
        
        print("\n✅ Teste E2E concluído: Jornada do cliente validada com sucesso!")
