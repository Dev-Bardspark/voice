import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Speech to Text",
    page_icon="🎤"
)

# Initialize session state
if "transcript" not in st.session_state:
    st.session_state.transcript = ""

st.title("🎤 Speech to Text Test")

# HTML component
html_code = """
<div style="text-align: center; padding: 20px;">
    <button onclick="startRecording()" 
        style="background-color: #4CAF50; color: white; padding: 15px 30px; font-size: 18px; border: none; border-radius: 5px; margin: 10px; cursor: pointer;">
        🎤 Start
    </button>
    
    <button onclick="stopRecording()" 
        style="background-color: #f44336; color: white; padding: 15px 30px; font-size: 18px; border: none; border-radius: 5px; margin: 10px; cursor: pointer;">
        ⏹️ Stop
    </button>
    
    <div id="status" style="margin: 20px; font-size: 16px;"></div>
    <div id="transcript" style="border:1px solid #ddd; padding:20px; min-height:100px;"></div>
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
    };
    
    recognition.onend = function() {
        document.getElementById('status').innerHTML = '⏹️ Stopped';
        if (finalTranscript) {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: finalTranscript.trim()
            }, '*');
        }
    };
    
    recognition.onresult = function(event) {
        let interim = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            if (event.results[i].isFinal) {
                finalTranscript += event.results[i][0].transcript + ' ';
            } else {
                interim += event.results[i][0].transcript;
            }
        }
        document.getElementById('transcript').innerHTML = 
            'Final: ' + finalTranscript + '<br>Interim: ' + interim;
    };
} else {
    document.getElementById('status').innerHTML = '❌ Not supported';
}

function startRecording() { finalTranscript = ''; recognition.start(); }
function stopRecording() { recognition.stop(); }
</script>
"""

# Get the transcript from component
result = components.html(html_code, height=400)

# Update session state if we got a result
if result:
    st.session_state.transcript = result

# DISPLAY THE OUTPUT CLEARLY
st.markdown("---")
st.header="📤 OUTPUT (for your other app)")  # <--- CHANGE THIS LINE

col1, col2 = st.columns(2)

with col1:
    st.subheader("Current Transcript Value")
    st.code(f"st.session_state.transcript = '{st.session_state.transcript}'")
    
    st.subheader("How to use in your app")
    st.code("""
# In your other app, just use:
transcript = st.session_state.transcript
if transcript:
    # Do something with the transcript
    print(transcript)
    """, language="python")

with col2:
    st.subheader("Live Preview")
    if st.session_state.transcript:
        st.success(f"📝 You said: {st.session_state.transcript}")
    else:
        st.info("Click Start, speak, then click Stop")

# Test button
if st.button("Test Output"):
    st.write(f"The transcript value is: '{st.session_state.transcript}'")
