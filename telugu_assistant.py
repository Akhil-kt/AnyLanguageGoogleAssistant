from record import record
from google.cloud import speech_v1
from google.cloud.speech_v1 import enums
from google.cloud import translate_v2
import google.oauth2.credentials
import os
import logging
import grpc
import click
import io
import json
from textinput import SampleTextAssistant
from telugu_speaker import Speaker
import html
import inflect

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/AKHIL/Development/telugu_google_assistant/TeluguAssistant-08f29b5f5e2f.json"

translate_client_to_en = translate_v2.Client(target_language='en')
translate_client_to_te = translate_v2.Client(target_language='te')

def nums2words(string):
    words = string.split()
    engine = inflect.engine()
    
    for i in range(len(words)):
        if any(map(str.isdigit, words[i])):
            words[i] = engine.number_to_words(words[i])
    string = " "
    return string.join(words)


def transcribe(local_file_path):
    """
    Transcribe a short audio file using synchronous speech recognition

    Args:
      local_file_path Path to local audio file, e.g. /path/audio.wav
    """

    client = speech_v1.SpeechClient()

    # local_file_path = 'resources/brooklyn_bridge.raw'

    # The language of the supplied audio
    language_code = "te-IN"

    # Sample rate in Hertz of the audio data sent
    sample_rate_hertz = 16000

    # Encoding of audio data sent. This sample sets this explicitly.
    # This field is optional for FLAC and WAV audio formats.
    encoding = enums.RecognitionConfig.AudioEncoding.LINEAR16
    config = {
        "language_code": language_code,
        "sample_rate_hertz": sample_rate_hertz,
        "encoding": encoding,
    }
    with io.open(local_file_path, "rb") as f:
        content = f.read()
    audio = {"content": content}

    response = client.recognize(config, audio)
    for result in response.results:
        # First alternative is the most probable result
        alternative = result.alternatives[0]
        return (u"{}".format(alternative.transcript))

credentials = os.path.join(click.get_app_dir('google-oauthlib-tool'),
                                   'credentials.json')
# Load OAuth 2.0 credentials.
try:
    with open(credentials, 'r') as f:
        credentials = google.oauth2.credentials.Credentials(token=None,
                                                            **json.load(f))
        http_request = google.auth.transport.requests.Request()
        credentials.refresh(http_request)
except Exception as e:
    logging.error('Error loading credentials: %s', e)
    logging.error('Run google-oauthlib-tool to initialize '
                    'new OAuth 2.0 credentials.')
    

# Create an authorized gRPC channel.
grpc_channel = google.auth.transport.grpc.secure_authorized_channel(
        credentials, http_request, "embeddedassistant.googleapis.com")
logging.info('Connecting to %s', "embeddedassistant.googleapis.com")


with SampleTextAssistant("en-US", "warm-torus-272916-macbook-pro-49fjm4", "warm-torus-272916", False,
                             grpc_channel, 60 * 3 + 5) as assistant:
        speaker = Speaker()
        while True:
            click.pause(info="Press any key to initiate a new request")
            record("output.wav")
            text_to_translate = transcribe("output.wav")
            english_text = translate_client_to_en.translate(text_to_translate)
            english_text['translatedText'] = html.unescape(english_text["translatedText"])

            click.echo('<you> %s' % text_to_translate)
            click.echo('<you> %s' % english_text['translatedText'])
            response_text, response_html = assistant.assist(text_query=english_text['translatedText'])                
            if response_text:
                response_text = nums2words(response_text)
                response_text_telugu = translate_client_to_te.translate(response_text)
                speaker.speak(response_text_telugu["translatedText"])
                click.echo('<@assistant> %s' % response_text)
                click.echo('<@assistant> %s' % response_text_telugu["translatedText"])
            