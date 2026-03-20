import streamlit as st
import streamlit.components.v1 as components
import tempfile
import os
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Speech to Text App",
    page_icon="🎤",
    layout="wide"
)

# Title and description
st.title("🎤 Speech to Text Converter")
st.markdown("Convert your speech to text using various methods")

# Sidebar for configuration
st.sidebar.header("Settings")
method = st.sidebar.selectbox(
    "Choose Method",
    ["Built-in Voice Input (Streamlit)", "Browser Speech Recognition", "Upload Audio File"]
)

# Method 1: Built-in Streamlit Voice Input
if method == "Built-in Voice Input (Streamlit)":
    st.header("Built-in Voice Input")
    st.info("Click the microphone icon in the chat input below and start speaking")
    
    # Using Streamlit's built-in voice input
    prompt = st.chat_input(
        "Click the microphone and speak...", 
        accept_voice=True
    )
    
    if prompt:
        st.success(f"You said: {prompt}")
        
        # Add to conversation history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display conversation
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

# Method 2: Browser Speech Recognition
elif method == "Browser Speech Recognition":
    st.header("Browser Speech Recognition")
    st.info("Click 'Start Recording' and allow microphone access")
    
    # Custom HTML component for speech recognition
    speech_html = """
    <div style="padding: 20px; border: 2px solid #4CAF50; border-radius: 10px; text-align: center;">
        <h3>Speech Recognition</h3>
        <button id="startBtn" onclick="startRecording()" style="background-color: #4CAF50; color: white; padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer;">🎤 Start Recording</button>
        <button id="stopBtn" onclick="stopRecording()" style="background-color: #f44336; color: white; padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer;">⏹️ Stop Recording</button>
        <p style="margin-top: 20px; font-size: 18px;">Transcript:</p>
        <div id="transcript" style="border: 1px solid #ddd; padding: 15px; min-height: 100px; border-radius: 5px; background-color: #f9f9f9; font-size: 16px;"></div>
        <div id="status" style="margin-top: 10px; color: #666;"></div>
    </div>

    <script>
        let recognition = null;
        let finalTranscript = '';
        
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            
            recognition.onstart = function() {
                document.getElementById('status').innerHTML = '🎤 Listening...';
                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
            };
            
            recognition.onend = function() {
                document.getElementById('status').innerHTML = '⏹️ Stopped';
                document.getElementById('startBtn').disabled = false;
                document.getElementById('stopBtn').disabled = true;
            };
            
            recognition.onresult = function(event) {
                let interimTranscript = '';
                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript + ' ';
                    } else {
                        interimTranscript += event.results[i][0].transcript;
                    }
                }
                document.getElementById('transcript').innerHTML = 
                    '<strong>Final:</strong> ' + finalTranscript + '<br>' +
                    '<strong>Interim:</strong> ' + interimTranscript;
                
                // Send final transcript to Streamlit
                if (finalTranscript) {
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: finalTranscript
                    }, '*');
                }
            };
            
            recognition.onerror = function(event) {
                document.getElementById('status').innerHTML = '❌ Error: ' + event.error;
            };
        } else {
            document.getElementById('status').innerHTML = '❌ Speech recognition not supported in this browser. Please use Chrome.';
        }
        
        function startRecording() {
            if (recognition) {
                finalTranscript = '';
                document.getElementById('transcript').innerHTML = '';
                recognition.start();
            }
        }
        
        function stopRecording() {
            if (recognition) {
                recognition.stop();
            }
        }
    </script>
    """
    
    # Display the speech recognition component
    transcript = components.html(speech_html, height=400)
    
    if transcript:
        st.text_area("Final Transcript:", transcript, height=100)
        
        # Save to session state
        if "browser_transcripts" not in st.session_state:
            st.session_state.browser_transcripts = []
        st.session_state.browser_transcripts.append(transcript)
        
        # Download button
        st.download_button(
            label="📥 Download Transcript",
            data=transcript,
            file_name="transcript.txt",
            mime="text/plain"
        )

# Method 3: Upload Audio File
else:
    st.header("Upload Audio File")
    st.info("Upload an audio file to convert to text")
    
    # Try to import required libraries
    try:
        import speech_recognition as sr
        from pydub import AudioSegment
        import io
        
        uploaded_file = st.file_uploader(
            "Choose an audio file", 
            type=['wav', 'mp3', 'm4a', 'ogg', 'flac']
        )
        
        if uploaded_file is not None:
            # Display audio player
            st.audio(uploaded_file)
            
            # Convert button
            if st.button("🔄 Convert to Text"):
                with st.spinner("Converting speech to text..."):
                    try:
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_path = tmp_file.name
                        
                        # Convert to WAV if needed
                        if not uploaded_file.name.endswith('.wav'):
                            audio = AudioSegment.from_file(tmp_path)
                            wav_path = tmp_path + '.wav'
                            audio.export(wav_path, format='wav')
                        else:
                            wav_path = tmp_path
                        
                        # Initialize recognizer
                        recognizer = sr.Recognizer()
                        
                        # Read audio file
                        with sr.AudioFile(wav_path) as source:
                            # Adjust for ambient noise
                            recognizer.adjust_for_ambient_noise(source, duration=0.5)
                            audio_data = recognizer.record(source)
                        
                        # Try multiple recognition engines
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("Google Speech Recognition")
                            try:
                                text = recognizer.recognize_google(audio_data)
                                st.success(text)
                                
                                # Download button for Google result
                                st.download_button(
                                    label="📥 Download (Google)",
                                    data=text,
                                    file_name="google_transcript.txt",
                                    mime="text/plain",
                                    key="google_download"
                                )
                            except sr.UnknownValueError:
                                st.error("Google Speech Recognition could not understand audio")
                            except sr.RequestError as e:
                                st.error(f"Could not request results from Google Speech Recognition service; {e}")
                        
                        with col2:
                            st.subheader("Sphinx (Offline)")
                            try:
                                text = recognizer.recognize_sphinx(audio_data)
                                st.success(text)
                                
                                # Download button for Sphinx result
                                st.download_button(
                                    label="📥 Download (Sphinx)",
                                    data=text,
                                    file_name="sphinx_transcript.txt",
                                    mime="text/plain",
                                    key="sphinx_download"
                                )
                            except:
                                st.info("Sphinx offline recognition not available. Install with: pip install pocketsphinx")
                        
                        # Clean up temporary files
                        os.unlink(tmp_path)
                        if uploaded_file.name.endswith('.wav'):
                            os.unlink(wav_path)
                            
                    except Exception as e:
                        st.error(f"Error processing audio: {str(e)}")
    
    except ImportError as e:
        st.warning("⚠️ Additional libraries needed for audio file processing.")
        st.code("""
        # Install required libraries:
        pip install SpeechRecognition pydub
        
        # For MP3 support:
        pip install ffmpeg
        
        # For offline recognition (optional):
        pip install pocketsphinx
        """)
        
        # Still allow file upload but show limited functionality
        uploaded_file = st.file_uploader("Choose an audio file", type=['wav', 'mp3'])
        if uploaded_file:
            st.audio(uploaded_file)
            st.info("Please install the required libraries to enable transcription.")

# Footer with instructions
st.markdown("---")
st.markdown("### 📝 Instructions")
with st.expander("Click to see instructions"):
    st.markdown("""
    **For Built-in Voice Input:**
    - Click the microphone icon in the chat input
    - Speak clearly
    - Click the send button or press Enter when done
    
    **For Browser Speech Recognition:**
    - Click 'Start Recording' and allow microphone access
    - Speak clearly
    - Click 'Stop Recording' when finished
    - The transcript will appear in real-time
    
    **For Audio File Upload:**
    - Upload a supported audio file (WAV, MP3, M4A, OGG, FLAC)
    - Click 'Convert to Text'
    - Download the transcript
    """)

# Sidebar info
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "This app converts speech to text using multiple methods. "
    "Choose the method that works best for your needs!"
)

# Requirements info
st.sidebar.markdown("### Requirements")
st.sidebar.code("""
streamlit
SpeechRecognition
pydub
pocketsphinx (optional)
""")
