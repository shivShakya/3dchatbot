import requests
import os
unreal_labs_key = os.getenv("Unreal_labs_Key")
def generate_speech_with_unrealspeech(
    text, 
    voice_id="Scarlett", 
    bitrate="128k", 
    speed="-0.03", 
    pitch="1.16", 
    timestamp_type="word", 
    authorization_token=unreal_labs_key
):
 
    url = "https://api.v7.unrealspeech.com/speech"
    
    payload = {
        "Text": text,
        "VoiceId": voice_id,
        "Bitrate": bitrate,
        "Speed": speed,
        "Pitch": pitch,
        "TimestampType": timestamp_type
    }

    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {authorization_token}"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None
