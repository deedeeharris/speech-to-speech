import streamlit as st
import requests
import json
from pydub import AudioSegment
import io

def speech_to_speech(audio_file, voice_id, api_key):
    sts_url = f"https://api.elevenlabs.io/v1/speech-to-speech/{voice_id}/stream"
    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key
    }
    data = {
        "model_id": "eleven_english_sts_v2",
        "voice_settings": json.dumps({
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True
        })
    }
    files = {
        "audio": audio_file
    }
    response = requests.post(sts_url, headers=headers, data=data, files=files, stream=True)
    if response.ok:
        return io.BytesIO(response.content)
    else:
        st.error("Failed to process audio: " + response.text)
        return None

def change_pitch(audio_bytes, octaves=-0.1):
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
    new_sample_rate = int(audio.frame_rate * (2.0 ** octaves))
    low_pitch_audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
    return low_pitch_audio

def main():
    st.title("Audio Processing App")
    
    # Password protection
    correct_password = st.secrets["password"]
    password = st.text_input("Enter your password", type="password")
    
    if password != correct_password:
        st.error("The password you entered is incorrect.")
        return
    
    st.write("Upload an audio file to process it with Eleven Labs Speech-to-Speech and adjust its pitch using Pydub.")

    uploaded_file = st.file_uploader("Choose an audio file", type=['mp3', 'wav', 'ogg', 'm4a'])
    octave_shift = st.slider("Select pitch shift in octaves:", -1.0, 1.0, -0.1)

    if uploaded_file is not None:
        with st.spinner("Processing audio..."):
            processed_audio = speech_to_speech(uploaded_file, st.secrets["voice_id"], st.secrets["api_key"])
            if processed_audio is not None:
                st.audio(processed_audio, format='audio/mp3', start_time=0)
                
                with st.spinner("Changing pitch..."):
                    pitched_audio = change_pitch(processed_audio.getvalue(), octaves=octave_shift)
                    pitched_audio_bytes = io.BytesIO()
                    pitched_audio.export(pitched_audio_bytes, format="mp3")
                    pitched_audio_bytes.seek(0)
                    
                    st.audio(pitched_audio_bytes, format='audio/mp3', start_time=0)
                    
                    st.download_button(
                        label="Download Processed Audio",
                        data=pitched_audio_bytes,
                        file_name="processed_audio.mp3",
                        mime="audio/mp3"
                    )

if __name__ == "__main__":
    main()
