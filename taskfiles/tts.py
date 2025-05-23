import os
from elevenlabs.client import ElevenLabs
from taskfiles.fallback import generate_speech_with_unrealspeech

elaven_labs_key = os.getenv("Eleven_labs_Key")
elaven_labs_voice_id = os.getenv("Elaven_labs_voice_id")
client = ElevenLabs(api_key=elaven_labs_key)


def useElavenlabsVoice(request):
    try:
#        response = client.text_to_speech.convert_with_timestamps(
#            voice_id=elaven_labs_voice_id,
#            output_format="mp3_44100_128",
#            text=request['message'],
#            model_id="eleven_flash_v2_5"
#        )
#        return response

        fallback_response = generate_speech_with_unrealspeech(request['message'])
        return fallback_response

    except KeyError as e:
        print(f"Error: Missing expected key {e} in the request")
    except Exception as e:
        print(f"Error with ElevenLabs API: {e}")
        print("Falling back to UnrealSpeech...")
    
    try:

        response = client.text_to_speech.convert_with_timestamps(
            voice_id=elaven_labs_voice_id,
            output_format="mp3_44100_128",
            text=request['message'],
            model_id="eleven_flash_v2_5"
        )
        return response

#       fallback_response = generate_speech_with_unrealspeech(request['message'])
#       return fallback_response
    except Exception as e:
        print(f"Error with UnrealSpeech fallback: {e}")
        return None
