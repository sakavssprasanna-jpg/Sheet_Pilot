import io
import wave
import json
import logging
from typing import Optional
from pydantic import BaseModel, Field
from src.ai.gemini_client import get_gemini_client, sanitize_gemini_schema

# Try importing google.genai safely
try:
    from google import genai
    from google.genai import types
    GENAI_INSTALLED = True
except ImportError:
    GENAI_INSTALLED = False

logger = logging.getLogger(__name__)

class VoiceTranscriptionResponse(BaseModel):
    transcript: str
    language: str
    confidence: str # "High", "Medium", "Low", or "Transcript ready for review"
    duration: float
    success: bool
    error: Optional[str] = None

class GeminiTranscriptionResult(BaseModel):
    transcript: str = Field(description="The exact text transcribed from the audio in its original spoken language. Preserve technical terms.")
    language: str = Field(description="The primary language detected in the audio.")
    confidence: str = Field(description="The confidence rating: 'High', 'Medium', or 'Low'.")

def estimate_duration(audio_bytes: bytes, mime_type: str = "audio/wav") -> float:
    """Estimate the duration of the audio in seconds in a safe cross-platform manner."""
    try:
        with wave.open(io.BytesIO(audio_bytes), 'rb') as wav:
            frames = wav.getnframes()
            rate = wav.getframerate()
            if rate > 0:
                return round(frames / float(rate), 2)
    except Exception:
        pass
        
    file_size = len(audio_bytes)
    if "webm" in mime_type:
        return round(file_size / 6000.0, 2) # assumed average ~48kbps for Opus WebM
    elif "ogg" in mime_type:
        return round(file_size / 8000.0, 2) # assumed average ~64kbps for Opus Ogg
    else:
        return round(file_size / 176000.0, 2) # fallback for uncompressed 16-bit PCM

def validate_audio(audio_bytes: bytes, mime_type: str) -> Optional[str]:
    """Validate audio inputs for common failure modes (silence, corruption, size, length)."""
    if not audio_bytes:
        return "Audio recording is empty."
    if len(audio_bytes) < 120:
        return "Audio data is too short or corrupted."
        
    duration = estimate_duration(audio_bytes, mime_type)
    if duration > 60.0:
        return f"Audio duration ({duration:.1f}s) exceeds the maximum limit of 60 seconds."
        
    return None

def transcribe_audio(audio_bytes: bytes, mime_type: str = "audio/wav", language: str = "English") -> VoiceTranscriptionResponse:
    """
    Transcribes audio bytes into text using the speech_recognition package (Google Web Speech API),
    avoiding the consumption of the Gemini reasoning API key quota.
    """
    import speech_recognition as sr
    duration = estimate_duration(audio_bytes, mime_type)
    
    # 1. Validate Audio
    validation_error = validate_audio(audio_bytes, mime_type)
    if validation_error:
        return VoiceTranscriptionResponse(
            transcript="",
            language=language,
            confidence="Low",
            duration=duration,
            success=False,
            error=validation_error
        )
        
    # Map friendly language name to Google STT language codes
    lang_mapping = {
        "English": "en-US",
        "Telugu": "te-IN",
        "Hindi": "hi-IN"
    }
    lang_code = lang_mapping.get(language, "en-US")
    
    r = sr.Recognizer()
    try:
        # Wrap bytes in BytesIO for AudioFile
        audio_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)
            
        # Perform Web Speech transcription (free, no API key required)
        transcript = r.recognize_google(audio_data, language=lang_code)
        transcript = transcript.strip()
        
        if not transcript:
            return VoiceTranscriptionResponse(
                transcript="",
                language=language,
                confidence="Low",
                duration=duration,
                success=False,
                error="Audio appears to be silent or contains no recognizable speech."
            )
            
        return VoiceTranscriptionResponse(
            transcript=transcript,
            language=language,
            confidence="High",
            duration=duration,
            success=True
        )
        
    except sr.UnknownValueError:
        return VoiceTranscriptionResponse(
            transcript="",
            language=language,
            confidence="Low",
            duration=duration,
            success=False,
            error="Speech recognition could not understand the audio. Please speak more clearly."
        )
    except sr.RequestError as e:
        logger.error(f"Google Speech Recognition service error: {e}")
        return VoiceTranscriptionResponse(
            transcript="",
            language=language,
            confidence="Low",
            duration=duration,
            success=False,
            error=f"Speech recognition service unavailable: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error during audio transcription: {e}")
        return VoiceTranscriptionResponse(
            transcript="",
            language=language,
            confidence="Low",
            duration=duration,
            success=False,
            error=f"Transcription failed: {str(e)}"
        )
