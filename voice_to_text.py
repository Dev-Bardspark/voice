import streamlit as st
import speech_recognition as sr
import tempfile
import os
from datetime import datetime

st.set_page_config(page_title="Speech to Text", page_icon="🎤", layout="wide")

# ====================== SESSION STATE ======================
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "full_audio" not in st.session_state:
    st.session_state.full_audio = b""
if "history" not in st.session_state:
    st.session_state.history = []
if "recording_count" not in st.session_state:
    st.session_state.recording_count = 0
if "is_recording" not in st.session_state:
    st.session_state.is_recording = False

st.title("🎤 Speech to Text - Dictation Mode")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎙️ Record Audio")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("▶️ Start Recording", type="primary", use_container_width=True, disabled=st.session_state.is_recording):
            st.session_state.is_recording = True
            st.rerun()

    with c2:
        if st.button("⏹️ Stop Recording", use_container_width=True, disabled=not st.session_state.is_recording):
            st.session_state.is_recording = False
            st.rerun()

    with c3:
        if st.button("🔄 Continue Recording", use_container_width=True, disabled=st.session_state.is_recording):
            st.session_state.is_recording = True
            st.rerun()

    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.transcript = ""
        st.session_state.full_audio = b""
        st.rerun()

    # Audio Input
    if st.session_state.is_recording:
        new_audio = st.audio_input("Speak now... (recording active)", label_visibility="collapsed")
        
        if new_audio is not None:
            st.session_state.full_audio += new_audio.getvalue()

            with st.spinner("Transcribing..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                        f.write(st.session_state.full_audio)
                        tmp_path = f.name

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
                    st.success("✅ Transcription updated!")

                except sr.UnknownValueError:
                    st.warning("Could not understand the audio.")
                except Exception as e:
                    st.error(f"Error: {e}")
                finally:
                    if 'tmp_path' in locals() and os.path.exists(tmp_path):
                        os.unlink(tmp_path)

with col2:
    st.subheader("📝 Current Transcript")
    if st.session_state.transcript:
        edited = st.text_area("Edit if needed:", st.session_state.transcript, height=180)
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
    else:
        st.info("Click **Start Recording**, speak, then click **Stop Recording**.")

# History
st.markdown("---")
st.subheader("📜 History")
if st.session_state.history:
    for i, item in enumerate(reversed(st.session_state.history[-5:])):
        with st.expander(f"{item['time']} — {item['text'][:60]}..."):
            st.write(item['text'])
            if st.button("Load", key=f"load_{i}"):
                st.session_state.transcript = item['text']
                st.rerun()

# Final Output
st.markdown("---")
st.header("📤 FINAL OUTPUT FOR YOUR OTHER APP")
st.success(f"**st.session_state.transcript =** \"{st.session_state.transcript}\"")
st.code("""
transcript = st.session_state.transcript
if transcript:
    print(transcript)
    # Use the text here
""", language="python")
