import streamlit as st
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
from pydub import AudioSegment
import tempfile
import os
from datetime import datetime

# ====================== SESSION STATE ======================
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "recording_count" not in st.session_state:
    st.session_state.recording_count = 0

st.set_page_config(page_title="Speech to Text", page_icon="🎤", layout="wide")

st.title("🎤 Speech to Text Converter")
st.markdown("---")

with st.sidebar:
    st.header("📊 Stats")
    st.metric("Total Recordings", st.session_state.recording_count)
    st.metric("Transcript Length", len(st.session_state.transcript))
    st.info("Make sure your browser allows microphone access")

# ====================== RECORDING ======================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎙️ Record Audio")
    
    audio_bytes = audio_recorder(
        text="Click to record",
        recording_color="#ff4b4b",
        neutral_color="#6c757d",
        icon_size="4x"
    )

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        st.info(f"Raw audio received: {len(audio_bytes):,} bytes")

        with st.spinner("Processing audio and transcribing..."):
            try:
                # Convert to proper WAV using pydub
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_in:
                    tmp_in.write(audio_bytes)
                    input_path = tmp_in.name

                audio = AudioSegment.from_file(input_path)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_out:
                    clean_path = tmp_out.name
                    audio.export(clean_path, format="wav", parameters=["-ac", "1", "-ar", "16000"])

                # Transcribe
                recognizer = sr.Recognizer()
                with sr.AudioFile(clean_path) as source:
                    audio_data = recognizer.record(source)
                    text = recognizer.recognize_google(audio_data, language="en-US")

                # Save
                st.session_state.transcript = text.strip()
                st.session_state.recording_count += 1
                st.session_state.history.append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "text": text.strip()
                })

                st.success("✅ Transcription successful!")

            except sr.UnknownValueError:
                st.error("❌ Could not understand the audio. Try speaking louder/clearer.")
            except sr.RequestError as e:
                st.error(f"❌ Google API error: {e}")
            except Exception as e:
                st.error(f"❌ Processing error: {str(e)}")
                st.info("Try recording again — short & clear speech works best.")
            finally:
                for path in [input_path, clean_path] if 'input_path' in locals() else []:
                    if os.path.exists(path):
                        os.unlink(path)

with col2:
    st.subheader("📝 Current Transcript")
    if st.session_state.transcript:
        edited = st.text_area("Edit if needed:", st.session_state.transcript, height=180)
        if edited != st.session_state.transcript:
            st.session_state.transcript = edited

        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾 Save to History", use_container_width=True):
                st.session_state.history.append({"time": datetime.now().strftime("%H:%M:%S"), "text": st.session_state.transcript})
                st.success("Saved!")
        with c2:
            st.download_button("📥 Download", st.session_state.transcript, 
                               f"transcript_{datetime.now().strftime('%Y%m%d_%H%M')}.txt", 
                               "text/plain", use_container_width=True)
    else:
        st.info("Record audio on the left → transcript appears here")

# History + Final Output (same as before)
st.markdown("---")
st.subheader("📜 History")
if st.session_state.history:
    for i, item in enumerate(reversed(st.session_state.history[-5:])):
        with st.expander(f"{item['time']} — {item['text'][:60]}..."):
            st.write(item['text'])
            if st.button("Load", key=f"load_{i}"):
                st.session_state.transcript = item['text']
                st.rerun()
    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()

st.markdown("---")
st.header("📤 FINAL OUTPUT FOR YOUR OTHER APP")
st.success(f"**st.session_state.transcript =** \"{st.session_state.transcript}\"")
