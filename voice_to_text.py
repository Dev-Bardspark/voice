import streamlit as st
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
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

st.set_page_config(
    page_title="Speech to Text",
    page_icon="🎤",
    layout="wide"
)

st.title("🎤 Speech to Text Converter")
st.markdown("---")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("📊 Stats")
    st.metric("Total Recordings", st.session_state.recording_count)
    st.metric("Transcript Length", len(st.session_state.transcript))
    
    st.markdown("---")
    st.header("ℹ️ Instructions")
    st.markdown("""
    1. Click the microphone button  
    2. Allow microphone access  
    3. Speak clearly  
    4. Click button again to stop  
    5. Text will appear below
    """)
    st.info("🔸 Best results for recordings under 50 seconds\n🔸 Longer recordings are automatically split")

# ====================== MAIN CONTENT ======================
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

        with st.spinner("🎙️ Converting speech to text... (splitting long recordings)"):
            try:
                # Save audio to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    tmp_file.write(audio_bytes)
                    original_path = tmp_file.name

                recognizer = sr.Recognizer()
                full_transcript = ""

                # Chunk settings
                CHUNK_DURATION = 45  # seconds - safe for Google API

                with sr.AudioFile(original_path) as source:
                    audio_duration = source.DURATION
                    
                    if audio_duration > 55:
                        st.warning(f"⚠️ Recording is {audio_duration:.1f} seconds long. Processing in chunks for better accuracy...")

                    offset = 0
                    while offset < audio_duration:
                        chunk_duration = min(CHUNK_DURATION, audio_duration - offset)
                        
                        source.seek(offset)
                        audio_chunk = recognizer.record(source, duration=chunk_duration)
                        
                        try:
                            text = recognizer.recognize_google(audio_chunk, language="en-US")
                            full_transcript += text + " "
                        except sr.UnknownValueError:
                            full_transcript += "[unclear section] "
                        except Exception:
                            full_transcript += "[error in section] "
                        
                        offset += chunk_duration

                final_text = full_transcript.strip()

                # Update session state
                st.session_state.transcript = final_text
                st.session_state.recording_count += 1
                
                st.session_state.history.append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "text": final_text
                })

                st.success("✅ Conversion complete!")

            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
            finally:
                # Clean up temp file
                if 'original_path' in locals() and os.path.exists(original_path):
                    os.unlink(original_path)

with col2:
    st.subheader("📝 Current Transcript")
    if st.session_state.transcript:
        edited_text = st.text_area(
            "Edit if needed:", 
            st.session_state.transcript, 
            height=180,
            key="transcript_area"
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
                st.success("Saved to history!")
        with col_b:
            st.download_button(
                label="📥 Download",
                data=st.session_state.transcript,
                file_name=f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    else:
        st.info("No transcript yet — record something above.")

# ====================== HISTORY ======================
st.markdown("---")
st.subheader("📜 History")

if st.session_state.history:
    for i, item in enumerate(reversed(st.session_state.history[-5:])):
        with st.expander(f"{item['time']} — {item['text'][:60]}..."):
            st.write(item['text'])
            if st.button("Load into Editor", key=f"load_{i}"):
                st.session_state.transcript = item['text']
                st.rerun()
    
    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.rerun()
else:
    st.info("Your recording history will appear here.")

# ====================== FINAL OUTPUT SECTION ======================
st.markdown("---")
st.header("📤 FINAL OUTPUT FOR YOUR OTHER APP")

st.success(f"**st.session_state.transcript =** \"{st.session_state.transcript}\"")

st.code("""
# In your other app, simply do this:

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

transcript = st.session_state.transcript

if transcript:
    st.write("User said:", transcript)
    # Process the transcript here...
""", language="python")
