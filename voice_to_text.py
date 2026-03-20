import streamlit as st
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder  # CHANGED THIS LINE
import tempfile
import os
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="Speech to Text Converter",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        padding: 10px;
    }
    .recording-box {
        border: 3px solid #ff4b4b;
        border-radius: 10px;
        padding: 20px;
        background-color: #fff0f0;
    }
    .success-box {
        border: 3px solid #4CAF50;
        border-radius: 10px;
        padding: 20px;
        background-color: #f0fff0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'transcripts' not in st.session_state:
    st.session_state.transcripts = []
if 'current_text' not in st.session_state:
    st.session_state.current_text = ""
if 'recording_started' not in st.session_state:
    st.session_state.recording_started = False

# Title and header
st.title("🎤 Speech to Text Converter")
st.markdown("### Convert your speech to text in real-time")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📋 Instructions")
    st.markdown("""
    1. **Click the microphone button** below to start recording
    2. **Allow microphone access** when prompted
    3. **Speak clearly** into your microphone
    4. **Click the button again** to stop recording
    5. **Click 'Convert to Text'** to transcribe
    """)
    
    st.markdown("---")
    st.header="📊 Stats"
    st.metric("Total Recordings", len(st.session_state.transcripts))
    
    if st.session_state.transcripts:
        if st.button("Clear All History"):
            st.session_state.transcripts = []
            st.session_state.current_text = ""
            st.rerun()
    
    st.markdown("---")
    st.markdown("### About")
    st.info(
        "This app uses Google Speech Recognition to convert "
        "your speech to text. Internet connection required."
    )

# Main content area
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown="### 🎙️ Recording"
    
    # Audio recorder
    audio_bytes = audio_recorder(
        text="Click to Record",
        recording_color="#ff4b4b",
        neutral_color="#6c757d",
        icon_name="microphone",
        icon_size="4x",
        pause_threshold=2.0
    )
    
    if audio_bytes:
        st.session_state.recording_started = True
        st.audio(audio_bytes, format="audio/wav")
        
        # Save audio info
        audio_size = len(audio_bytes) / 1024  # KB
        st.caption(f"Recording size: {audio_size:.1f} KB")
        
        # Convert button
        if st.button("🔄 Convert to Text", use_container_width=True):
            with st.spinner("Converting speech to text..."):
                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    tmp_file.write(audio_bytes)
                    tmp_path = tmp_file.name
                
                try:
                    # Initialize recognizer
                    recognizer = sr.Recognizer()
                    
                    # Read audio file
                    with sr.AudioFile(tmp_path) as source:
                        # Adjust for ambient noise
                        recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        audio_data = recognizer.record(source)
                    
                    # Try multiple recognition engines
                    try:
                        # Google Speech Recognition
                        text = recognizer.recognize_google(audio_data)
                        st.session_state.current_text = text
                        
                        # Add to history
                        st.session_state.transcripts.append({
                            'text': text,
                            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'method': 'Google'
                        })
                        
                    except sr.UnknownValueError:
                        st.error("❌ Could not understand the audio. Please try again.")
                    except sr.RequestError as e:
                        st.error(f"❌ Could not reach Google Speech Recognition service: {e}")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                    
                except Exception as e:
                    st.error(f"❌ Error processing audio: {str(e)}")
                
                finally:
                    # Clean up temp file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
    
    else:
        if not st.session_state.recording_started:
            st.info("👆 Click the microphone button above to start recording")
        else:
            st.warning("No recording detected. Please try again.")

with col2:
    st.markdown="### 📝 Current Transcript"
    
    if st.session_state.current_text:
        with st.container():
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.write(st.session_state.current_text)
            
            # Download button
            st.download_button(
                label="📥 Download as TXT",
                data=st.session_state.current_text,
                file_name=f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="recording-box">', unsafe_allow_html=True)
        st.write("No transcript yet. Record something and click Convert!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown="### 📜 History"
    
    if st.session_state.transcripts:
        for i, item in enumerate(reversed(st.session_state.transcripts[-5:])):
            with st.expander(f"Recording {len(st.session_state.transcripts) - i} - {item['time']}"):
                st.write(item['text'])
                if st.button(f"Load", key=f"load_{i}"):
                    st.session_state.current_text = item['text']
                    st.rerun()
    else:
        st.info("No recordings yet")

# File upload option
st.markdown("---")
st.markdown("### 📁 Upload Audio File")

uploaded_file = st.file_uploader(
    "Choose an audio file",
    type=['wav', 'mp3', 'm4a', 'flac', 'ogg'],
    help="Upload an audio file to transcribe"
)

if uploaded_file:
    col1, col2 = st.columns(2)
    
    with col1:
        st.audio(uploaded_file)
    
    with col2:
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
        st.write(f"**Filename:** {uploaded_file.name}")
        st.write(f"**Size:** {file_size:.2f} MB")
        
        if st.button("🔄 Transcribe File", use_container_width=True):
            with st.spinner("Transcribing audio file..."):
                # Save uploaded file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_input:
                    tmp_input.write(uploaded_file.getvalue())
                    input_path = tmp_input.name
                
                try:
                    # Convert to wav if needed
                    if not uploaded_file.name.endswith('.wav'):
                        from pydub import AudioSegment
                        audio = AudioSegment.from_file(input_path)
                        wav_path = input_path + '.wav'
                        audio.export(wav_path, format='wav')
                    else:
                        wav_path = input_path
                    
                    # Transcribe
                    recognizer = sr.Recognizer()
                    with sr.AudioFile(wav_path) as source:
                        recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        audio_data = recognizer.record(source)
                        text = recognizer.recognize_google(audio_data)
                    
                    st.success("✅ Transcription complete!")
                    st.text_area("Transcribed Text:", text, height=150)
                    
                    # Add to history
                    st.session_state.transcripts.append({
                        'text': text,
                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'method': 'File Upload'
                    })
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                
                finally:
                    # Clean up
                    for path in [input_path, wav_path if 'wav_path' in locals() else None]:
                        if path and os.path.exists(path):
                            os.unlink(path)

# Footer
st.markdown("---")
st.markdown(
    "<center>Made with Streamlit • Speech Recognition • 2026</center>",
    unsafe_allow_html=True
)
