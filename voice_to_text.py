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

st.title("🎤 Speech to Text Converter")
st.markdown("---")

with st.sidebar:
    st.header("📊 Stats")
    st.metric("Total Recordings", st.session_state.recording_count)
    st.metric("Transcript Length", len(st.session_state.transcript))
    st.info("Speak continuously.\nIt now waits ~10 seconds before stopping.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎙️ Record Audio")

    if st.button("🗑️ Clear & Start Again", type="primary", use_container_width=True):
        st.session_state.transcript = ""
        st.rerun()

    audio_bytes = audio_recorder(
        text="Click to record • Speak naturally",
        recording_color="#ff4b4b",
        neutral_color="#6c757d",
        icon_size="4x",
        pause_threshold=10.0,          # Longer pause tolerance
        energy_threshold=(-0.6, 1.0)
    )

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")

        with st.spinner("Converting to text..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    tmp_file.write(audio_bytes)
                    tmp_path = tmp_file.name

                recognizer = sr.Recognizer()
                with sr.AudioFile(tmp_path) as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio_data = recognizer.record(source)

                text = recognizer.recognize_google(audio_data)

                st.session_state.transcript = text
                st.session_state.recording_count += 1
                st.session_state.history.append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "text": text
                })

                st.success("✅ Conversion complete! Use 'Clear & Start Again' for new recording.")

            except sr.UnknownValueError:
                st.error("❌ Could not understand audio. Speak louder and clearer.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
            finally:
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.unlink(tmp_path)

with col2:
    st.subheader("📝 Current Transcript")
    if st.session_state.transcript:
        edited_text = st.text_area("Edit if needed:", st.session_state.transcript, height=160)
        if edited_text != st.session_state.transcript:
            st.session_state.transcript = edited_text

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
    else:
        st.info("Record on the left side")

# History + Final Output
st.markdown("---")
st.subheader("📜 History")
if st.session_state.history:
    for i, item in enumerate(reversed(st.session_state.history[-5:])):
        with st.expander(f"{item['time']} — {item['text'][:60]}..."):
            st.write(item['text'])
            if st.button("Load", key=f"load_{i}"):
                st.session_state.transcript = item['text']
                st.rerun()

st.markdown("---")
st.header("📤 FINAL OUTPUT FOR YOUR OTHER APP")
st.success(f"**st.session_state.transcript =** \"{st.session_state.transcript}\"")
st.code("""
transcript = st.session_state.transcript
if transcript:
    print(transcript)
""", language="python")
