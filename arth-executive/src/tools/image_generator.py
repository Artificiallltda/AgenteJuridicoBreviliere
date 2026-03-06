from langchain_core.tools import tool
from openai import OpenAI
import os
import uuid
import base64
from src.config import settings

@tool
def generate_image(prompt: str) -> str:
    """
    Desenha ou gera uma imagem baseada em um texto e retorna o link (URL) da imagem pronta.
    Use essa ferramenta APENAS quando o usu\'E1rio pedir explicitamente para "desenhar", "criar imagem", 
    "gerar foto", "imaginar", "ilustrar" algo.
    O 'prompt' deve ser uma descri\'E7\'E3o extremamente rica, detalhada e em ingl\^es (traduza do usu\'E1rio se precisar) 
    do que ele quer na imagem.
    """
    if not settings.OPENAI_API_KEY:
        return "Erro: Chave da OpenAI n\'E3o configurada para gerar imagens."
        
    try:    
        url = 'https://api.openai.com/v1/images/generations'
        headers = {
            'Authorization': f'Bearer {settings.OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': 'gpt-image-1.5',
            'prompt': prompt,
            'n': 1,
            'size': '1024x1024'
        }

        import httpx
        with httpx.Client(timeout=60.0) as client:
            response = client.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            # gpt-image-1.5 devolve b64_json na base
            resp_data = response.json()
            b64_data = resp_data["data"][0].get("b64_json")
            
            if not b64_data:
                # Fallback caso volte url (milagre)
                image_url = resp_data["data"][0].get("url")
                if image_url: return f"Link da imagem: {image_url}"
                return "Falha t\u00e9cnica. O modelo n\u00e3o retornou nem URL nem dados b64."
            
            data_dir = os.path.join(os.getcwd(), "data", "outputs")
            os.makedirs(data_dir, exist_ok=True)
            filename = f"img_{uuid.uuid4().hex[:8]}.png"
            filepath = os.path.join(data_dir, filename)

            with open(filepath, "wb") as f:
                f.write(base64.b64decode(b64_data))
            
        return (
            f"A imagem foi gerada com sucesso nos bastidores. "
            f"Agora escreva uma BREVE APRESENTAÇÃO da imagem para o usuário (1 a 2 linhas), "
            f"descrevendo o que foi criado de forma simpática e entusiasmada. "
            f"E no FINAL da sua resposta, cole EXATAMENTE esta tag: <SEND_FILE:{filename}>\n"
            f"NÃO crie links markdown."
        )
    except Exception as e:
        return f"Houve um erro ao tentar gerar a imagem: {str(e)}"
