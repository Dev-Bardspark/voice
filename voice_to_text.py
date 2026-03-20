import streamlit as st
import speech_recognition as sr
from streamlit_audio_recorder import audio_recorder
import tempfile
import os

# Page config
st.set_page_config(
    page_title="Speech to Text",
    page_icon="🎤",
    layout="centered"
)

# Title
st.title("🎤 Speech to Text Converter")
st.markdown("---")

# Initialize recognizer
recognizer = sr.Recognizer()

# Create tabs for different input methods
tab1, tab2 = st.tabs(["🎙️ Record Live", "📁 Upload File"])

# Tab 1: Live Recording
with tab1:
    st.write("Click the microphone button below to start recording")
    
    # Audio recorder widget
    audio_bytes = audio_recorder(
        text="",
        recording_color="#ff4b4b",
        neutral_color="#6c757d",
        icon_name="microphone",
        icon_size="2x"
    )
    
    if audio_bytes:
        # Play recorded audio
        st.audio(audio_bytes, format="audio/wav")
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        # Convert to text
        if st.button("Convert to Text", key="convert_live"):
            with st.spinner("Converting speech to text..."):
                try:
                    with sr.AudioFile(tmp_path) as source:
                        audio_data = recognizer.record(source)
                        text = recognizer.recognize_google(audio_data)
                        
                        st.success("✅ Conversion successful!")
                        st.text_area("Transcribed Text:", text, height=150)
                        
                        # Download button
                        st.download_button(
                            "📥 Download Text",
                            text,
                            file_name="transcript.txt"
                        )
                except sr.UnknownValueError:
                    st.error("Could not understand audio")
                except sr.RequestError:
                    st.error("Could not reach Google Speech Recognition service")
                finally:
                    os.unlink(tmp_path)

# Tab 2: File Upload
with tab2:
    st.write("Upload an audio file")
    
    uploaded_file = st.file_uploader(
        "Choose an audio file",
        type=['wav', 'mp3', 'm4a', 'flac']
    )
    
    if uploaded_file:
        st.audio(uploaded_file)
        
        if st.button("Convert to Text", key="convert_file"):
            with st.spinner("Converting speech to text..."):
                try:
                    # Save uploaded file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    # Convert to text
                    with sr.AudioFile(tmp_path) as source:
                        audio_data = recognizer.record(source)
                        text = recognizer.recognize_google(audio_data)
                        
                        st.success("✅ Conversion successful!")
                        st.text_area("Transcribed Text:", text, height=150)
                        
                        # Download button
                        st.download_button(
                            "📥 Download Text",
                            text,
                            file_name="transcript.txt"
                        )
                except sr.UnknownValueError:
                    st.error("Could not understand audio")
                except sr.RequestError:
                    st.error("Could not reach Google Speech Recognition service")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

# Sidebar with instructions
with st.sidebar:
    st.header("📖 Instructions")
    st.markdown("""
    **Live Recording:**
    1. Click the microphone button
    2. Allow microphone access
    3. Speak clearly
    4. Click button again to stop
    5. Click "Convert to Text"
    
    **File Upload:**
    1. Upload audio file
    2. Click "Convert to Text"
    
    **Supported formats:**
    - WAV, MP3, M4A, FLAC
    """)
    
    st.markdown("---")
    st.header="About"
    st.info(
        "This app uses Google Speech Recognition "
        "to convert speech to text. Internet connection required."
    )
