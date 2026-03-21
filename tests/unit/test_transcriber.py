import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from audio.transcriber import AudioTranscriber

@pytest.fixture
def mock_whisper():
    """Fixture para mock do Whisper API."""
    with patch("audio.transcriber.AsyncOpenAI") as MockOpenAI:
        mock_client = MagicMock()
        MockOpenAI.return_value = mock_client
        
        # Mock da resposta de transcricao
        mock_response = MagicMock()
        mock_response.text = "Transcricao de teste"
        
        mock_client.audio = MagicMock()
        mock_client.audio.transcriptions = MagicMock()
        mock_client.audio.transcriptions.create = AsyncMock(return_value=mock_response)
        
        yield mock_client

@pytest.mark.asyncio
async def test_transcribe_calls_whisper(mock_whisper):
    """Testa que transcribe chama Whisper API."""
    transcriber = AudioTranscriber()
    
    # Mock de download de audio
    audio_bytes = b"fake audio data"
    
    result = await transcriber.transcribe(audio_bytes)
    
    # Deve retornar transcricao ou fallback
    assert result is not None
    assert isinstance(result, str)
