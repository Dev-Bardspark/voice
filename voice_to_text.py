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
    """)
    st.info("🔸 Recordings longer than ~50 seconds are automatically split into chunks")

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

        with st.spinner("🎙️ Converting to text... (splitting long recordings if needed)"):
            try:
                # Save original recording
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(audio_bytes)
                    temp_wav = tmp.name

                # Load with pydub
                audio = AudioSegment.from_wav(temp_wav)
                duration_sec = len(audio) / 1000

                recognizer = sr.Recognizer()
                full_transcript = ""

                CHUNK_MS = 45000  # 45 seconds per chunk

                if duration_sec > 55:
                    st.warning(f"⚠️ Recording is {duration_sec:.1f} seconds long → splitting into chunks")

                for i in range(0, len(audio), CHUNK_MS):
                    chunk = audio[i : i + CHUNK_MS]
                    
                    # Export chunk to temporary wav
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as chunk_file:
                        chunk_path = chunk_file.name
                        chunk.export(chunk_path, format="wav")

                    # Recognize chunk
                    with sr.AudioFile(chunk_path) as source:
                        audio_data = recognizer.record(source)
                        try:
                            text = recognizer.recognize_google(audio_data, language="en-US")
                            full_transcript += text + " "
                        except sr.UnknownValueError:
                            full_transcript += "[unclear] "
                        except Exception:
                            pass

                    # Clean up chunk
                    if os.path.exists(chunk_path):
                        os.unlink(chunk_path)

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
                st.error(f"❌ Error: {str(e)}")
            finally:
                # Clean up original temp file
                if 'temp_wav' in locals() and os.path.exists(temp_wav):
                    os.unlink(temp_wav)

with col2:
    st.subheader("📝 Current Transcript")
    if st.session_state.transcript:
        edited_text = st.text_area(
            "Edit if needed:", 
            st.session_state.transcript, 
            height=180
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
        st.info("Record something to see the transcript here.")

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
    st.info("History will appear here.")

# ====================== FINAL OUTPUT ======================
st.markdown("---")
st.header("📤 FINAL OUTPUT FOR YOUR OTHER APP")
st.success(f"**st.session_state.transcript =** \"{st.session_state.transcript}\"")
st.code("""
# In your other app:
transcript = st.session_state.transcript
if transcript:
    # Use the transcript here
    st.write(transcript)
""", language="python")
