import streamlit as st
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
import tempfile
import os
from datetime import datetime

st.set_page_config(
    page_title="Speech to Text",
    page_icon="🎤",
    layout="wide"
)

# ====================== SESSION STATE ======================
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "recording_count" not in st.session_state:
    st.session_state.recording_count = 0

st.title("🎤 Speech to Text Converter")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📊 Stats")
    st.metric("Total Recordings", st.session_state.recording_count)
    st.metric("Transcript Length", len(st.session_state.transcript))
    
    st.markdown("---")
    st.header("ℹ️ Instructions")
    st.markdown("""
    1. Click microphone button  
    2. Allow microphone access  
    3. Speak continuously  
    4. Click button again to stop  
    5. Use the buttons below to clear or restart
    """)

# ====================== MAIN CONTENT ======================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎙️ Record Audio")
    
    # === TWO CONTROL BUTTONS ===
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("🗑️ Clear Transcript", use_container_width=True):
            st.session_state.transcript = ""
            st.rerun()
    
    with btn_col2:
        if st.button("🔄 Clear & Start Again", type="primary", use_container_width=True):
            st.session_state.transcript = ""
            st.session_state.last_audio_bytes = None
            st.rerun()

    # Audio Recorder
    audio_bytes = audio_recorder(
        text="Click to record (speak continuously)",
        recording_color="#ff4b4b",
        neutral_color="#6c757d",
        icon_size="4x",
        pause_threshold=6.0,
        energy_threshold=(-0.5, 1.0)
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
                
                st.success("✅ Conversion complete!")

            except sr.UnknownValueError:
                st.error("❌ Could not understand audio — speak louder and clearer")
            except sr.RequestError:
                st.error("❌ Speech recognition service error")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
            finally:
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.unlink(tmp_path)

with col2:
    st.subheader("📝 Current Transcript")
    if st.session_state.transcript:
        edited_text = st.text_area(
            "Edit if needed:",
            st.session_state.transcript,
            height=160
        )
        if edited_text != st.session_state.transcript:
            st.session_state.transcript = edited_text

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("💾 Save to History", use_container_width=True):
                st.session_state.history.append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "text": st.session_state.transcript
                })
                st.success("Saved!")
        with col_b:
            st.download_button(
                label="📥 Download",
                data=st.session_state.transcript,
                file_name=f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    else:
        st.info("Record something above")

# ====================== OUTPUT TESTER ======================
st.markdown("---")
st.header("🔍 OUTPUT TESTER")
col_test1, col_test2 = st.columns(2)
with col_test1:
    st.subheader("Current Value in Session State")
    st.code(f"st.session_state.transcript = '{st.session_state.transcript}'")
    st.metric("Character Count", len(st.session_state.transcript))

with col_test2:
    if st.button("🔴 CLICK TO TEST OUTPUT", use_container_width=True):
        if st.session_state.transcript:
            st.success("✅ OUTPUT IS WORKING!")
            st.json({"transcript": st.session_state.transcript})
        else:
            st.warning("⚠️ No transcript yet")

# ====================== HISTORY ======================
st.markdown("---")
st.subheader("📜 History")
if st.session_state.history:
    for i, item in enumerate(reversed(st.session_state.history[-5:])):
        with st.expander(f"{item['time']} - {item['text'][:50]}..."):
            st.write(item['text'])
            if st.button("Load", key=f"load_{i}"):
                st.session_state.transcript = item['text']
                st.rerun()
    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()

# ====================== FINAL OUTPUT ======================
st.markdown("---")
st.header("📤 FINAL OUTPUT FOR YOUR OTHER APP")
st.success(f"**st.session_state.transcript =** \"{st.session_state.transcript}\"")
st.code("""
# In your other app, just use:
user_input = st.session_state.transcript
if user_input:
    print(user_input)
""", language="python")
