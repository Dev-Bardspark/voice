import streamlit as st
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
import tempfile
import os
from datetime import datetime

st.set_page_config(page_title="Speech to Text", page_icon="🎤", layout="wide")

# Session State
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "recording_count" not in st.session_state:
    st.session_state.recording_count = 0
if "accumulated_audio" not in st.session_state:
    st.session_state.accumulated_audio = None

st.title("🎤 Speech to Text Converter")
st.markdown("---")

with st.sidebar:
    st.header("📊 Stats")
    st.metric("Total Recordings", st.session_state.recording_count)
    st.metric("Transcript Length", len(st.session_state.transcript))
    st.info("You can now pause up to 10 seconds and continue recording")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎙️ Record Audio")

    # Control buttons
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Clear Everything", use_container_width=True):
            st.session_state.transcript = ""
            st.session_state.accumulated_audio = None
            st.rerun()
    
    with c2:
        if st.button("🔄 Continue Recording", type="primary", use_container_width=True):
            st.rerun()   # This forces the recorder to restart listening

    # Main Recorder
    audio_bytes = audio_recorder(
        text="Click to record • You can pause up to 10 seconds",
        recording_color="#ff4b4b",
        neutral_color="#6c757d",
        icon_size="4x",
        pause_threshold=10.0,          # Wait 10 seconds of silence
        energy_threshold=(-0.6, 1.0)
    )

    if audio_bytes:
        # Combine with previous audio if exists
        if st.session_state.accumulated_audio is not None:
            combined = st.session_state.accumulated_audio + audio_bytes
        else:
            combined = audio_bytes

        st.session_state.accumulated_audio = combined
        st.audio(combined, format="audio/wav")

        with st.spinner("Converting to text..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                    f.write(combined)
                    tmp_path = f.name

                r = sr.Recognizer()
                with sr.AudioFile(tmp_path) as source:
                    r.adjust_for_ambient_noise(source, duration=0.5)
                    audio_data = r.record(source)

                text = r.recognize_google(audio_data)

                st.session_state.transcript = text
                st.session_state.recording_count += 1

                st.session_state.history.append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "text": text
                })

                st.success("✅ Transcription updated!")

            except sr.UnknownValueError:
                st.error("❌ Could not understand audio")
            except Exception as e:
                st.error(f"❌ Error: {e}")
            finally:
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.unlink(tmp_path)

with col2:
    st.subheader("📝 Current Transcript")
    if st.session_state.transcript:
        edited = st.text_area("Edit if needed:", st.session_state.transcript, height=160)
        if edited != st.session_state.transcript:
            st.session_state.transcript = edited

        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾 Save to History", use_container_width=True):
                st.session_state.history.append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "text": st.session_state.transcript
                })
                st.success("Saved!")
        with c2:
            st.download_button("📥 Download", st.session_state.transcript,
                               f"transcript_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                               "text/plain", use_container_width=True)

# History and Final Output sections (kept short)
st.markdown("---")
st.subheader("📜 History")
if st.session_state.history:
    for i, item in enumerate(reversed(st.session_state.history[-5:])):
        with st.expander(f"{item['time']} - {item['text'][:50]}..."):
            st.write(item['text'])
            if st.button("Load", key=f"load_{i}"):
                st.session_state.transcript = item['text']
                st.rerun()

st.markdown("---")
st.header("📤 FINAL OUTPUT FOR YOUR OTHER APP")
st.success(f"**st.session_state.transcript =** \"{st.session_state.transcript}\"")
