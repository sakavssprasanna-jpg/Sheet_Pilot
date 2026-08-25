import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import speech_recognition as sr
from src.voice.processor import estimate_duration, validate_audio, transcribe_audio
from src.ai.gemini_client import query_gemini_intelligence
from src.execution.operation_engine import execute_operation
from src.state import SessionStateManager

class TestVoiceProcessor(unittest.TestCase):
    def test_estimate_duration_wav_fallback(self):
        # Create a mock 16-bit PCM WAV header + some bytes
        # Standard WAV PCM mono 16kHz is 32000 bytes/sec. Let's pass 32000 bytes
        mock_bytes = b"0" * 32000
        duration = estimate_duration(mock_bytes, "audio/wav")
        # Since it's not a real wav with valid header, it will fallback to file_size / 176000.0
        expected = round(32000 / 176000.0, 2)
        self.assertEqual(duration, expected)

    def test_estimate_duration_webm(self):
        # 12000 bytes WebM file should be roughly 12000 / 6000 = 2 seconds
        mock_bytes = b"0" * 12000
        duration = estimate_duration(mock_bytes, "audio/webm")
        self.assertEqual(duration, 2.0)

    def test_validate_audio_empty(self):
        err = validate_audio(b"", "audio/wav")
        self.assertIn("empty", err.lower())

    def test_validate_audio_corrupted(self):
        err = validate_audio(b"too_short", "audio/wav")
        self.assertIn("too short or corrupted", err.lower())

    def test_validate_audio_excessive(self):
        # Generate 12 MB of mock WAV bytes, which exceeds 60s
        large_bytes = b"0" * (176000 * 61)
        err = validate_audio(large_bytes, "audio/wav")
        self.assertIn("exceeds the maximum limit", err.lower())

    @patch("speech_recognition.Recognizer")
    @patch("speech_recognition.AudioFile")
    def test_transcribe_audio_english(self, mock_audio_file, mock_recognizer_class):
        mock_recognizer = MagicMock()
        mock_recognizer.recognize_google.return_value = "Show the top 10 records by revenue"
        mock_recognizer_class.return_value = mock_recognizer
        
        # Audio must be >= 120 bytes
        wav_bytes = b"RIFF" + b"\x00" * 200
        res = transcribe_audio(wav_bytes, "audio/wav", language="English")
        
        self.assertTrue(res.success)
        self.assertEqual(res.transcript, "Show the top 10 records by revenue")
        self.assertEqual(res.language, "English")
        mock_recognizer.recognize_google.assert_called_once_with(unittest.mock.ANY, language="en-US")

    @patch("speech_recognition.Recognizer")
    @patch("speech_recognition.AudioFile")
    def test_transcribe_audio_telugu(self, mock_audio_file, mock_recognizer_class):
        mock_recognizer = MagicMock()
        mock_recognizer.recognize_google.return_value = "South region highest profit records"
        mock_recognizer_class.return_value = mock_recognizer
        
        wav_bytes = b"RIFF" + b"\x00" * 200
        res = transcribe_audio(wav_bytes, "audio/wav", language="Telugu")
        
        self.assertTrue(res.success)
        self.assertEqual(res.transcript, "South region highest profit records")
        self.assertEqual(res.language, "Telugu")
        mock_recognizer.recognize_google.assert_called_once_with(unittest.mock.ANY, language="te-IN")

    @patch("speech_recognition.Recognizer")
    @patch("speech_recognition.AudioFile")
    def test_transcribe_audio_hindi(self, mock_audio_file, mock_recognizer_class):
        mock_recognizer = MagicMock()
        mock_recognizer.recognize_google.return_value = "Show top records by revenue"
        mock_recognizer_class.return_value = mock_recognizer
        
        wav_bytes = b"RIFF" + b"\x00" * 200
        res = transcribe_audio(wav_bytes, "audio/wav", language="Hindi")
        
        self.assertTrue(res.success)
        self.assertEqual(res.transcript, "Show top records by revenue")
        self.assertEqual(res.language, "Hindi")
        mock_recognizer.recognize_google.assert_called_once_with(unittest.mock.ANY, language="hi-IN")

    @patch("speech_recognition.Recognizer")
    @patch("speech_recognition.AudioFile")
    @patch("src.voice.processor.get_gemini_client")
    def test_zero_gemini_calls_during_transcription(self, mock_get_client, mock_audio_file, mock_recognizer_class):
        mock_recognizer = MagicMock()
        mock_recognizer.recognize_google.return_value = "Hello"
        mock_recognizer_class.return_value = mock_recognizer
        
        wav_bytes = b"RIFF" + b"\x00" * 200
        res = transcribe_audio(wav_bytes, "audio/wav", language="English")
        
        self.assertTrue(res.success)
        mock_get_client.assert_not_called()

    @patch("speech_recognition.Recognizer")
    @patch("speech_recognition.AudioFile")
    def test_transcribe_unknown_value_error(self, mock_audio_file, mock_recognizer_class):
        mock_recognizer = MagicMock()
        mock_recognizer.recognize_google.side_effect = sr.UnknownValueError("Could not understand")
        mock_recognizer_class.return_value = mock_recognizer
        
        wav_bytes = b"RIFF" + b"\x00" * 200
        res = transcribe_audio(wav_bytes, "audio/wav", language="English")
        
        self.assertFalse(res.success)
        self.assertIn("could not understand", res.error.lower())

    @patch("speech_recognition.Recognizer")
    @patch("speech_recognition.AudioFile")
    def test_transcribe_request_error(self, mock_audio_file, mock_recognizer_class):
        mock_recognizer = MagicMock()
        mock_recognizer.recognize_google.side_effect = sr.RequestError("Service unavailable")
        mock_recognizer_class.return_value = mock_recognizer
        
        wav_bytes = b"RIFF" + b"\x00" * 200
        res = transcribe_audio(wav_bytes, "audio/wav", language="English")
        
        self.assertFalse(res.success)
        self.assertIn("service unavailable", res.error.lower())

    @patch("speech_recognition.Recognizer")
    @patch("speech_recognition.AudioFile")
    def test_transcribe_general_exception(self, mock_audio_file, mock_recognizer_class):
        mock_recognizer = MagicMock()
        mock_recognizer.recognize_google.side_effect = Exception("System crash")
        mock_recognizer_class.return_value = mock_recognizer
        
        wav_bytes = b"RIFF" + b"\x00" * 200
        res = transcribe_audio(wav_bytes, "audio/wav", language="English")
        
        self.assertFalse(res.success)
        self.assertIn("failed: system crash", res.error.lower())

    @unittest.mock.patch("src.ai.gemini_client.get_gemini_client")
    def test_voice_pipeline_integration(self, mock_get_client):
        # Setup mock client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        # Mock generate_content response
        mock_response = MagicMock()
        mock_response.text = '{"status": "success", "operation": {"intent": "filter_sort", "limit": 10, "explanation": "Show top 10 records by Revenue"}, "explanation": "Top 10 records", "language": "English", "error": null}'
        mock_client.models.generate_content.return_value = mock_response
        
        import streamlit as st
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        SessionStateManager.init_state()
        
        df = pd.DataFrame({
            "Revenue": [100, 200, 300, 400],
            "Product": ["A", "B", "C", "D"]
        })
        SessionStateManager.set_current_df(df)
        
        voice_transcript = "Show the top 10 records by revenue"
        ai_resp = query_gemini_intelligence(voice_transcript)
        
        self.assertEqual(ai_resp.status, "success")
        self.assertIsNotNone(ai_resp.operation)
        self.assertEqual(ai_resp.operation.limit, 10)
        
        res = execute_operation(ai_resp.operation, df)
        self.assertTrue(res.success)
        self.assertIsNotNone(res.result_dataframe)

    @unittest.mock.patch("src.ai.gemini_client.get_gemini_client")
    def test_voice_multilingual_transcript_accepted(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.text = '{"status": "success", "operation": {"intent": "filter_sort", "limit": 5, "explanation": "Show top 5 records with highest profit in South region"}, "explanation": "Top 5 profit in South", "language": "Telugu", "error": null}'
        mock_client.models.generate_content.return_value = mock_response
        
        import streamlit as st
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        SessionStateManager.init_state()
        
        df = pd.DataFrame({
            "Profit": [10, 20, 30],
            "Region": ["South", "South", "North"]
        })
        SessionStateManager.set_current_df(df)
        
        telugu_transcript = "South region lo highest profit vachina top 5 records chupinchu."
        ai_resp = query_gemini_intelligence(telugu_transcript)
        
        self.assertEqual(ai_resp.status, "success")
        self.assertEqual(ai_resp.language, "Telugu")

    def test_empty_transcript_handled(self):
        err = validate_audio(b"", "audio/wav")
        self.assertEqual(err, "Audio recording is empty.")

    @unittest.mock.patch("src.ai.gemini_client.get_gemini_client")
    def test_gemini_failure_handled_in_pipeline(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("API Quota Exceeded")
        
        import streamlit as st
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        SessionStateManager.init_state()
        SessionStateManager.set_current_df(pd.DataFrame({"A": [1]}))
        
        ai_resp = query_gemini_intelligence("Show top records")
        self.assertEqual(ai_resp.status, "ai_error")
        self.assertIn("Gemini API request failed", ai_resp.error)

    @unittest.mock.patch("src.ai.gemini_client.get_gemini_client")
    def test_text_command_works(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = '{"status": "success", "operation": {"intent": "filter_sort", "limit": 10, "explanation": "Show top 10"}, "explanation": "Top 10", "language": "English", "error": null}'
        mock_client.models.generate_content.return_value = mock_response
        
        import streamlit as st
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        SessionStateManager.init_state()
        SessionStateManager.set_current_df(pd.DataFrame({"A": [1]}))
        
        ai_resp = query_gemini_intelligence("Show top 10")
        self.assertEqual(ai_resp.status, "success")

    @patch("speech_recognition.Recognizer")
    @patch("speech_recognition.AudioFile")
    @patch("src.ai.gemini_client.get_gemini_client")
    def test_recording_created_does_not_call_gemini(self, mock_get_client, mock_audio_file, mock_recognizer_class):
        mock_recognizer = MagicMock()
        mock_recognizer.recognize_google.return_value = "Show records"
        mock_recognizer_class.return_value = mock_recognizer
        
        wav_bytes = b"RIFF" + b"\x00" * 200
        res = transcribe_audio(wav_bytes, "audio/wav", language="English")
        
        self.assertTrue(res.success)
        self.assertEqual(res.transcript, "Show records")
        mock_get_client.assert_not_called()

if __name__ == "__main__":
    unittest.main()
