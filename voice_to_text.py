import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

st.set_page_config(
    page_title="Speech to Text",
    page_icon="🎤",
    layout="wide"
)

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []
if "current_text" not in st.session_state:
    st.session_state.current_text = ""

# Title
st.title("🎤 Speech to Text Converter")
st.markdown("---")

# HTML/JavaScript for speech recognition
speech_html = """
<div style="text-align: center; padding: 20px;">
    <button onclick="startRecording()" 
        style="background-color: #4CAF50; color: white; padding: 15px 30px; font-size: 18px; border: none; border-radius: 5px; margin: 10px; cursor: pointer;">
        🎤 Start Recording
    </button>
    
    <button onclick="stopRecording()" 
        style="background-color: #f44336; color: white; padding: 15px 30px; font-size: 18px; border: none; border-radius: 5px; margin: 10px; cursor: pointer;">
        ⏹️ Stop Recording
    </button>
    
    <div id="status" style="margin: 20px; font-size: 16px; color: #666;"></div>
    
    <div style="border: 2px solid #ddd; border-radius: 10px; padding: 20px; min-height: 150px; background-color: #f9f9f9; font-size: 18px; text-align: left;">
        <div id="transcript"></div>
    </div>
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
        document.getElementById('status').style.color = '#4CAF50';
    };
    
    recognition.onend = function() {
        document.getElementById('status').innerHTML = '⏹️ Stopped';
        document.getElementById('status').style.color = '#666';
    };
    
    recognition.onresult = function(event) {
        let interimTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript + ' ';
            } else {
                interimTranscript += transcript;
            }
        }
        
        document.getElementById('transcript').innerHTML = 
            '<strong>Final:</strong> ' + finalTranscript + '<br>' +
            '<strong>Interim:</strong> ' + interimTranscript;
        
        // Send to Streamlit
        if (finalTranscript) {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: finalTranscript
            }, '*');
        }
    };
    
    recognition.onerror = function(event) {
        document.getElementById('status').innerHTML = 'Error: ' + event.error;
        document.getElementById('status').style.color = '#f44336';
    };
} else {
    document.getElementById('status').innerHTML = '❌ Speech recognition not supported. Please use Chrome, Edge, or Safari.';
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

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎙️ Recording")
    transcript = components.html(speech_html, height=400)
    
    if transcript:
        st.session_state.current_text = transcript
        st.success("✅ Speech captured!")

with col2:
    st.subheader="📝 Current Text"
    
    if st.session_state.current_text:
        st.text_area("", st.session_state.current_text, height=150)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("💾 Save", use_container_width=True):
                st.session_state.history.append({
                    "text": st.session_state.current_text,
                    "time": datetime.now().strftime("%H:%M:%S")
                })
                st.success("Saved!")
        with col_b:
            st.download_button(
                "📥 Download",
                st.session_state.current_text,
                file_name="transcript.txt",
                use_container_width=True
            )
    else:
        st.info("Click 'Start Recording' and speak")

# History section
st.markdown("---")
st.subheader="📜 History"

if st.session_state.history:
    for i, item in enumerate(reversed(st.session_state.history[-10:])):
        with st.expander(f"{item['time']} - {item['text'][:50]}..."):
            st.write(item['text'])
            if st.button("Load", key=f"load_{i}"):
                st.session_state.current_text = item['text']
                st.rerun()
else:
    st.info("No saved transcripts yet")

# Sidebar info
with st.sidebar:
    st.header="ℹ️ How to use"
    st.markdown("""
    1. Click **Start Recording**
    2. Allow microphone access
    3. Speak clearly
    4. Click **Stop Recording**
    5. Save or download your text
    """)
    
    st.markdown("---")
    st.metric("Total Recordings", len(st.session_state.history))
