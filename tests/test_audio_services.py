import unittest
from unittest.mock import patch, MagicMock, mock_open
from voycejotr.audio_services import convert_audio_to_text

class TestAudioServices(unittest.TestCase):

    @patch('voycejotr.audio_services.OpenAI')
    def test_convert_audio_to_text_success(self, mock_openai):
        # Mock the OpenAI client and the transcription response
        mock_transcription = MagicMock()
        mock_transcription.text = "This is a test transcription."
        mock_openai.audio.transcriptions.create.return_value = mock_transcription

        with patch('builtins.open', mock_open(read_data="data")) as mock_file:
            transcription = convert_audio_to_text(mock_openai, "fake_path_to_audio_file.webm")
        
        self.assertEqual(transcription, "This is a test transcription.")
        mock_file.assert_called_with("fake_path_to_audio_file.webm", "rb")

    def test_convert_audio_to_text_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            convert_audio_to_text(None, "fake_path_to_audio_file.webm")

    @patch('voycejotr.audio_services.OpenAI')
    def test_convert_audio_to_text_api_failure(self, mock_openai):
        # Mock the OpenAI client to raise an exception
        mock_openai.audio.transcriptions.create.side_effect = Exception("API error")
        
        with patch('builtins.open', mock_open(read_data="data")) as mock_file:
            with self.assertRaises(Exception):
                convert_audio_to_text(mock_openai, "fake_path_to_audio_file.webm")