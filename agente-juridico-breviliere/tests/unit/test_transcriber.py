import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from src.audio.transcriber import AudioTranscriber

@pytest.fixture
def mock_openai_local():
    with patch("src.audio.transcriber.AsyncOpenAI") as mock:
        client = MagicMock()
        client.audio = MagicMock()
        client.audio.transcriptions = MagicMock()
        client.audio.transcriptions.create = AsyncMock()
        mock.return_value = client
        yield client

@pytest.fixture
def transcriber(mock_openai_local):
    return AudioTranscriber()

@pytest.mark.asyncio
async def test_transcribe_calls_whisper(transcriber, mock_openai_local):
    mock_openai_local.audio.transcriptions.create.return_value = MagicMock(text="Transcricao de teste")
    
    with patch("os.unlink"):
        res = await transcriber.transcribe(b"fake_audio_bytes")
        assert res == "Transcricao de teste"
        assert mock_openai_local.audio.transcriptions.create.called

@pytest.mark.asyncio
async def test_transcribe_error_returns_fallback(transcriber, mock_openai_local):
    mock_openai_local.audio.transcriptions.create.side_effect = Exception("Whisper error")
    
    res = await transcriber.transcribe(b"fake_audio_bytes")
    assert res == "[Audio nao pode ser transcrito]"

@pytest.mark.asyncio
async def test_download_whatsapp_media(transcriber):
    # Mock httpx.AsyncClient().get
    mock_resp_meta = MagicMock()
    mock_resp_meta.json.return_value = {"url": "https://meta.cdn/audio.ogg"}
    mock_resp_meta.raise_for_status = MagicMock()
    
    mock_resp_audio = MagicMock()
    mock_resp_audio.content = b"audio_content"
    mock_resp_audio.raise_for_status = MagicMock()
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = [mock_resp_meta, mock_resp_audio]
        
        content = await transcriber.download_whatsapp_media("media_123")
        assert content == b"audio_content"
        assert mock_get.call_count == 2

@pytest.mark.asyncio
async def test_download_telegram_media(transcriber):
    mock_resp_path = MagicMock()
    mock_resp_path.json.return_value = {"result": {"file_path": "voices/v1.ogg"}}
    mock_resp_path.raise_for_status = MagicMock()
    
    mock_resp_audio = MagicMock()
    mock_resp_audio.content = b"tg_audio_content"
    mock_resp_audio.raise_for_status = MagicMock()
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = [mock_resp_path, mock_resp_audio]
        
        content = await transcriber.download_telegram_media("file_abc")
        assert content == b"tg_audio_content"
        assert mock_get.call_count == 2
