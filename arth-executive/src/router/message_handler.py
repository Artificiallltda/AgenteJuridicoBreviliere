from fastapi import APIRouter, Request, BackgroundTasks
import logging
from src.core.graph import build_arth_graph
from langchain_core.messages import HumanMessage
import httpx
import re
import os
import base64
from src.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Instancia o c\'E9rebro (em mem\'F3ria para este MVP)
arth_brain = build_arth_graph()

def get_tool_eta_message(tool_name: str) -> str:
    messages = {
        "search_web": "Estou vasculhando a internet para encontrar isso pra você... 🔍⏳",
        "generate_docx": "Estou formatando o documento. Jajá o arquivo fica pronto... 📄⏳",
        "generate_pdf": "Vou estruturar esse PDF detalhado! Fica pronto rapidinho... 📑⏳",
        "execute_python_code": "Carregando o console... Vou rodar um código Python para resolver isso... 💻⏳",
        "ask_chefia": "Legal, vou mandar uma mensagem pra ChefIA agora mesmo para puxar essa especialidade... 📞⏳",
        "generate_image": "Preparando os pincéis digitais! A imagem já vai sair do forno... 🎨⏳",
        "analyze_data_file": "Bip Bop... Vou cruzar esses dados e gerar os resultados pra você... 📊⏳",
        "schedule_reminder": "anotado! Estou registrando isso na minha agenda... 📅⏳",
        "generate_pptx": "Estruturando os slides! Sua apresentação já fica pronta... 📈🖼️⏳"
    }
    # Para ferramentas r\'e1pidas como get_current_time ou search_memory, n\'e3o enviamos push.
    return messages.get(tool_name, "")


async def execute_brain(user_id: str, text: str, channel: str, status_callback=None, user_name: str = "Usuário") -> str:
    """Função core para rodar o raciocínio independente do canal, com streaming de status."""
    logger.info(f"[{channel.upper()}] Processando mensagem de {user_name} ({user_id}): {text}")
    initial_state = {
        "messages": [HumanMessage(content=text)],
        "user_id": str(user_id),
        "channel": channel
    }
    
    # Adicionamos user_name na config invisível do bot
    config = {"configurable": {"thread_id": f"{channel}_{user_id}", "user_name": user_name}}
    
    try:
        # Controla quais ETAs já foram enviados para não spammar o usuário
        sent_etas = set()
        
        # Astream permite ler os eventos node-by-node
        async for event in arth_brain.astream(initial_state, config=config):
            for node, state_update in event.items():
                if node == "reason":
                    msg = state_update["messages"][-1]
                    if hasattr(msg, "tool_calls") and msg.tool_calls and status_callback:
                        for tool_call in msg.tool_calls:
                            tool_name = tool_call["name"]
                            if tool_name not in sent_etas:
                                eta_msg = get_tool_eta_message(tool_name)
                                if eta_msg:
                                    await status_callback(eta_msg)
                                    sent_etas.add(tool_name)
        
        # L\^e o estado final que ficou na mem\'f3ria do checkpointer
        final_state = await arth_brain.aget_state(config)
        return final_state.values["messages"][-1].content
            
    except Exception as e:
        import traceback
        logger.error(f"Erro crasso no execute_brain: {e}\nTraceback:\n{traceback.format_exc()}")
        return "Ops, meu sistema de raciocínio executivo teve uma falha técnica."

# ==========================================
# WHATSAPP (Evolution API)
# ==========================================

async def process_whatsapp_and_reply(user_name: str, text: str, remote_jid: str):
    async def send_status(msg: str):
        # Envia a mensagem de ETA no formato itálico
        await send_whatsapp_message(remote_jid, f"_{msg}_")
        
    ai_response = await execute_brain(user_id=remote_jid, text=text, channel="whatsapp", status_callback=send_status, user_name=user_name)
    
    # Remove backticks if the LLM returned `<SEND_FILE:..>` inside a markdown code block
    file_matches = re.findall(r'<SEND_FILE:([^>]+)>', ai_response)
    clean_text = re.sub(r'`?<SEND_FILE:[^>]+>`?', '', ai_response).strip()
    
    if clean_text:
        await send_whatsapp_message(remote_jid, clean_text)
        
    for file_name in file_matches:
        full_path = os.path.join(os.getcwd(), "data", "outputs", file_name.strip())
        await send_whatsapp_document(remote_jid, full_path)

async def send_whatsapp_message(remote_jid: str, text: str):
    if not settings.EVOLUTION_API_URL or not settings.EVOLUTION_API_KEY:
        logger.warning(f"[Mock] Whatsapp para {remote_jid}: {text}")
        return
        
    url = f"{settings.EVOLUTION_API_URL}/message/sendText/{settings.INSTANCE_NAME}"
    headers = {"apikey": settings.EVOLUTION_API_KEY, "Content-Type": "application/json"}
    payload = {"number": remote_jid, "options": {"delay": 1200, "presence": "composing"}, "textMessage": {"text": text}}
    
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload, headers=headers, timeout=10.0)
        except Exception as e:
            logger.error(f"Falha ao enviar mensagem Evolution API: {e}")

async def send_whatsapp_document(remote_jid: str, file_path: str):
    if not settings.EVOLUTION_API_URL or not settings.EVOLUTION_API_KEY:
        return
    if not os.path.exists(file_path):
        logger.error(f"Documento n\'E3o encontrado para envio: {file_path}")
        return
        
    mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if file_path.endswith(".png"): mime_type = "image/png"
    elif file_path.endswith(".pdf"): mime_type = "application/pdf"
    
    with open(file_path, "rb") as f:
        media_base64 = base64.b64encode(f.read()).decode("utf-8")
        
    url = f"{settings.EVOLUTION_API_URL}/message/sendMedia/{settings.INSTANCE_NAME}"
    headers = {"apikey": settings.EVOLUTION_API_KEY, "Content-Type": "application/json"}
    payload = {
        "number": remote_jid,
        "options": {"delay": 1200, "presence": "composing"},
        "mediaMessage": {
            "mediatype": "document",
            "fileName": os.path.basename(file_path),
            "media": f"data:{mime_type};base64,{media_base64}"
        }
    }
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload, headers=headers, timeout=30.0)
        except Exception as e:
            logger.error(f"Falha ao enviar documento Evolution: {e}")

@router.post("/whatsapp/webhook")
async def receive_whatsapp(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    if not isinstance(body, dict) or "data" not in body: return {"status": "ignored"}
    data = body.get("data", {})
    message_info = data.get("message", {})
    remote_jid = data.get("key", {}).get("remoteJid", "")
    push_name = data.get("pushName", "Usu\'E1rio")
    
    text = message_info.get("conversation", "")
    if "extendedTextMessage" in message_info and not text:
        text = message_info["extendedTextMessage"].get("text", "")
        
    if data.get("key", {}).get("fromMe") or not text: return {"status": "ignored"}
    background_tasks.add_task(process_whatsapp_and_reply, push_name, text, remote_jid)
    return {"status": "queued"}

# ==========================================
# TELEGRAM
# ==========================================

async def process_telegram_and_reply(user_name: str, text: str, chat_id: str):
    async def send_status(msg: str):
        # Envia a mensagem de ETA no formata itálico
        await send_telegram_message(chat_id, f"_{msg}_")
        
    ai_response = await execute_brain(user_id=chat_id, text=text, channel="telegram", status_callback=send_status, user_name=user_name)
    
    # Remove backticks se o LLM mandar a tag como c\'f3digo
    file_matches = re.findall(r'<SEND_FILE:([^>]+)>', ai_response)
    clean_text = re.sub(r'`?<SEND_FILE:[^>]+>`?', '', ai_response).strip()
    
    if clean_text:
        await send_telegram_message(chat_id, clean_text)
        
    for file_name in file_matches:
        full_path = os.path.join(os.getcwd(), "data", "outputs", file_name.strip())
        await send_telegram_document(chat_id, full_path)

async def send_telegram_message(chat_id: str, text: str):
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning(f"[Mock] Telegram para {chat_id}: {text}")
        return
        
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload, timeout=10.0)
        except Exception as e:
            logger.error(f"Falha ao enviar mensagem Telegram API: {e}")

async def send_telegram_document(chat_id: str, file_path: str):
    if not settings.TELEGRAM_BOT_TOKEN:
        return
    if not os.path.exists(file_path):
        logger.error(f"Documento n\'E3o encontrado para envio: {file_path}")
        return
        
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendDocument"
    async with httpx.AsyncClient() as client:
        try:
            with open(file_path, "rb") as f:
                # O telegram precisa ver o nome do arquivo para saber a extens\'E3o
                files = {"document": (os.path.basename(file_path), f)}
                data = {"chat_id": chat_id}
                await client.post(url, data=data, files=files, timeout=30.0)
        except Exception as e:
            logger.error(f"Falha ao enviar documento Telegram API: {e}")

@router.post("/telegram/webhook")
async def receive_telegram(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    if "message" not in body: return {"status": "ignored"}
    
    msg = body["message"]
    text = msg.get("text", "")
    chat_id = str(msg.get("chat", {}).get("id", ""))
    user_name = msg.get("from", {}).get("first_name", "Usu\'E1rio")
    
    if not text or not chat_id: return {"status": "ignored"}
    background_tasks.add_task(process_telegram_and_reply, user_name, text, chat_id)
    return {"status": "queued"}
