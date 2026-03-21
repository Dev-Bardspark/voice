import streamlit as st
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
from pydub import AudioSegment
import tempfile
import os
from datetime import datetime

st.set_page_config(page_title="Speech to Text", page_icon="🎤", layout="wide")

if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "recording_count" not in st.session_state:
    st.session_state.recording_count = 0

st.title("🎤 Speech to Text Converter")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎙️ Record Audio")

    if st.button("🗑️ Clear & Start Again", type="primary", use_container_width=True):
        st.session_state.transcript = ""
        st.rerun()

    audio_bytes = audio_recorder(
        text="Click to record • Speak clearly",
        recording_color="#ff4b4b",
        neutral_color="#6c757d",
        icon_size="4x",
        pause_threshold=8.0
    )

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        st.info(f"Audio size: {len(audio_bytes)/1024:.1f} KB")

        with st.spinner("Cleaning audio and transcribing..."):
            try:
                # Save raw audio
                with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
                    tmp.write(audio_bytes)
                    raw_path = tmp.name

                # Convert + clean with pydub
                audio = AudioSegment.from_file(raw_path)
                audio = audio.set_frame_rate(16000).set_channels(1).normalize()

                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as clean:
                    clean_path = clean.name
                    audio.export(clean_path, format="wav")

                # Transcribe
                recognizer = sr.Recognizer()
                with sr.AudioFile(clean_path) as source:
                    audio_data = recognizer.record(source)

                text = recognizer.recognize_google(audio_data)

                st.session_state.transcript = text
                st.session_state.recording_count += 1
                st.session_state.history.append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "text": text
                })

                st.success("✅ Transcription successful!")

            except sr.UnknownValueError:
                st.error("❌ Could not understand audio")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
            finally:
                for p in [raw_path, clean_path] if 'raw_path' in locals() else []:
                    if os.path.exists(p):
                        os.unlink(p)

with col2:
    st.subheader("📝 Current Transcript")
    if st.session_state.transcript:
        edited = st.text_area("Edit if needed:", st.session_state.transcript, height=160)
        if edited != st.session_state.transcript:
            st.session_state.transcript = edited
        st.download_button("📥 Download Transcript", st.session_state.transcript, 
                           f"transcript_{datetime.now().strftime('%Y%m%d_%H%M')}.txt", "text/plain")
    else:
        st.info("Record something on the left")

st.markdown("---")
st.header("📤 FINAL OUTPUT FOR YOUR OTHER APP")
st.success(f"**st.session_state.transcript =** \"{st.session_state.transcript}\"")
