from flask import Flask, jsonify, request
from google.oauth2 import service_account
from google.cloud import speech
from flask_restx import Resource, fields, Namespace
from app.extensions import api
from models.audio_preprocess import convert_to_mono

router = api.namespace('api', description='Semua Endpoint yang digunakan untuk aplikasi ini')

# Load the speech project service account credentials
client_file = 'utils/speech_credentials.json'
credentials = service_account.Credentials.from_service_account_file(client_file)

# Create the Speech-to-Text client
client = speech.SpeechClient(credentials=credentials)

@router.route('/')  # Decorate the function with the route
class Speech_to_text(Resource):
    def post(self):
        # Check if audio file is provided
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        # Get the audio file from the request
        audio_file = request.files['audio']

        # Load the mono audio file
        mono_audio = convert_to_mono(audio_file)

        # Read the content of the mono audio file
        
        content = mono_audio.read()
        mono_audio.seek(0)

        # Create RecognitionAudio object from the content
        audio = speech.RecognitionAudio(content=content)

        # Configure the recognition
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code='id-ID'
        )

        # Perform the speech recognition
        response = client.recognize(config=config, audio=audio)

        # Get the transcriptions from the response
        transcriptions = []
        for result in response.results:
            transcription = result.alternatives[0].transcript
            transcriptions.append(transcription)

        # Return the transcriptions as JSON
        return jsonify({'transcriptions': transcriptions}), 200
