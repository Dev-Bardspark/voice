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

# Initialize session state
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
    3. Speak clearly  
    4. Click button again to stop  
    5. Text appears below
    """)

# Main content
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
        
        with st.spinner("Converting to text..."):
            try:
                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    tmp_file.write(audio_bytes)
                    tmp_path = tmp_file.name

                recognizer = sr.Recognizer()
                with sr.AudioFile(tmp_path) as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio_data = recognizer.record(source)
                
                text = recognizer.recognize_google(audio_data)

                # === THIS WAS THE MAIN PROBLEM AREA ===
                st.session_state.transcript = text
                st.session_state.recording_count += 1
                
                st.session_state.history.append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "text": text
                })

                st.success("✅ Conversion complete!")

            except sr.UnknownValueError:
                st.error("❌ Could not understand audio")
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
            height=150
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
        st.info("No transcript yet - record something")

# OUTPUT TESTER
st.markdown("---")
st.header("🔍 OUTPUT TESTER")
col_test1, col_test2 = st.columns(2)

with col_test1:
    st.subheader("Current Value in Session State")
    st.code(f"st.session_state.transcript = '{st.session_state.transcript}'")
    st.metric("Character Count", len(st.session_state.transcript))

with col_test2:
    st.subheader("Verify Output")
    if st.button("🔴 CLICK TO TEST OUTPUT", use_container_width=True):
        if st.session_state.transcript:
            st.success("✅ OUTPUT IS WORKING!")
            st.json({"transcript": st.session_state.transcript})
        else:
            st.warning("⚠️ No transcript yet")

# History
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

# Final output section
st.markdown("---")
st.header("📤 FINAL OUTPUT FOR YOUR OTHER APP")
st.success(f"**st.session_state.transcript =** \"{st.session_state.transcript}\"")
st.code("""
# In your other app, just use:
user_input = st.session_state.transcript
if user_input:
    print(user_input)
    # Do something with it
""", language="python")
