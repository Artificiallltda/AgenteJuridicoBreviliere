from langchain_core.tools import tool
import httpx
import logging
from src.config import settings

logger = logging.getLogger(__name__)

@tool
def ask_chefia(query: str) -> str:
    """
    Delega uma pergunta ou tarefa para o ChefIA, o seu Agente Especialista em Gastronomia da Artificiall LTDA.
    Use esta ferramenta SEMPRE que o usu\'E1rio perguntar sobre receitas, ingredientes, dicas de culin\'E1ria, 
    restaurantes, ou qualquer coisa relacionada ao mundo gastron\'F4mico.
    O ChefIA \'E9 o especialista nisso, voc\'EA (Arth) apenas gerencia a requisi\'E7\'E3o.
    - query: A pergunta exata ou pedido gastron\'F4mico do usu\'E1rio (ex: "Me d\'EA uma receita de bolo de cenoura").
    """
    
    # URL provisoria do webhook do ChefIA (assumindo que roda na mesma m\'E1quina/servidor)
    # Se o ChefIA estiver no Telegram, a integra\'E7\'E3o pode ser adaptada.
    # Por enquanto, chamaremos a API REST interna do ChefIA caso exista.
    chefia_url = getattr(settings, "CHEFIA_API_URL", "http://localhost:8001/chat") 
    
    logger.info(f"Delegando para ChefIA: {query}")
    
    try:
        # Tenta uma chamada HTTP para a API do ChefIA local (mock para est\'E1gio atual)
        # return "Eu falei com o ChefIA e ele disse: [Resposta mockada de gastronomia]"
        
        # O c\'F3digo abaixo seria o real:
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(chefia_url, json={"message": query})
        #     return response.json().get("reply", "ChefIA n\'E3o soube responder.")
        
        return (
            "Eu entrei em contato com o ChefIA \u2014 nosso especialista em gastronomia \u2014 e ele recomendou "
            "isso para a sua solicitação gastronômica: 'Para um prato excelente, foque em ingredientes frescos e "
            "uma boa base de temperos. Desculpe não dar a receita completa agora, estou no modo de testes da integração.'\n\n"
            "(Nota do Sistema: Integra\'E7\'E3o mockada com sucesso. Substitua pelo endpoint real do ChefIA na ferramenta.)"
        )
    except Exception as e:
         return f"O ChefIA est\'E1 indispon\'EDvel no momento. Tente novamente mais tarde. Erro: {e}"
