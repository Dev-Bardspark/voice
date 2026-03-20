import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Speech to Text",
    page_icon="🎤",
    layout="wide"
)

# Initialize session state
if "transcript" not in st.session_state:
    st.session_state.transcript = ""

st.title("🎤 Speech to Text Test")

# ==================== HTML + JavaScript Component ====================
html_code = """
<div style="text-align: center; padding: 20px; font-family: sans-serif;">
    <button onclick="startRecording()" 
        style="background-color: #4CAF50; color: white; padding: 15px 32px; font-size: 18px; border: none; 
               border-radius: 8px; margin: 10px; cursor: pointer;">
        🎤 Start Recording
    </button>
   
    <button onclick="stopRecording()" 
        style="background-color: #f44336; color: white; padding: 15px 32px; font-size: 18px; border: none; 
               border-radius: 8px; margin: 10px; cursor: pointer;">
        ⏹️ Stop Recording
    </button>

    <div id="status" style="margin: 25px 0; font-size: 18px; font-weight: bold; min-height: 28px;"></div>
    
    <div id="transcript" style="border: 2px solid #ddd; border-radius: 8px; padding: 20px; 
                                min-height: 120px; background: #f9f9f9; text-align: left; 
                                white-space: pre-wrap; font-size: 16px;"></div>
</div>

<script>
let recognition = null;
let finalTranscript = '';

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
        document.getElementById('status').innerHTML = '🎤 Listening... (speak now)';
        document.getElementById('status').style.color = '#4CAF50';
    };

    recognition.onend = () => {
        document.getElementById('status').innerHTML = '⏹️ Stopped';
        document.getElementById('status').style.color = '#333';
        
        if (finalTranscript.trim()) {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: finalTranscript.trim()
            }, '*');
        }
    };

    recognition.onerror = (event) => {
        document.getElementById('status').innerHTML = `❌ Error: ${event.error}`;
        document.getElementById('status').style.color = 'red';
    };

    recognition.onresult = (event) => {
        let interim = '';
        finalTranscript = '';  // Rebuild final transcript every time for accuracy

        for (let i = 0; i < event.results.length; i++) {
            const transcriptPart = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcriptPart + ' ';
            } else {
                interim += transcriptPart;
            }
        }

        document.getElementById('transcript').innerHTML = 
            `<strong>Final:</strong> ${finalTranscript}<br><br>` +
            `<span style="color: #666;"><strong>Interim:</strong> ${interim}</span>`;
    };
} else {
    document.getElementById('status').innerHTML = '❌ Speech Recognition not supported in this browser';
}

function startRecording() {
    if (!recognition) return;
    finalTranscript = '';
    document.getElementById('transcript').innerHTML = '';
    recognition.start();
}

function stopRecording() {
    if (recognition) recognition.stop();
}
</script>
"""

# Render the component
components.html(html_code, height=420, scrolling=False)

# Listen for messages from the component (this is the key fix)
if "component_value" not in st.session_state:
    st.session_state.component_value = None

# This trick forces Streamlit to re-run when the JS posts a message
st.session_state.transcript = st.session_state.get("component_value", "")

# ====================== DISPLAY OUTPUT ======================
st.markdown("---")
st.header("📤 OUTPUT")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Current Transcript")
    if st.session_state.transcript:
        st.success(st.session_state.transcript)
    else:
        st.info("No transcript yet. Click **Start Recording**, speak, then **Stop Recording**.")

    st.subheader("How to use this in another app")
    st.code("""
import streamlit as st

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

# ... (your speech component here)

transcript = st.session_state.transcript
if transcript:
    st.write("You said:", transcript)
    # Do whatever you want with the text
""", language="python")

with col2:
    st.subheader("Live Preview")
    if st.session_state.transcript:
        st.success(f"✅ **You said:**\n\n{st.session_state.transcript}")
    else:
        st.info("🎙️ Speak after pressing Start")

# Optional test button
if st.button("🔄 Refresh Transcript"):
    st.rerun()
