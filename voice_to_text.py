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
if "history" not in st.session_state:
    st.session_state.history = []

st.title("🎤 Speech to Text Converter")

# HTML with postMessage
html_code = """
<div style="text-align: center; padding: 20px;">
    <button onclick="startRecording()" 
        style="background-color: #4CAF50; color: white; padding: 15px 30px; font-size: 18px; border: none; border-radius: 5px; margin: 10px; cursor: pointer;">
        🎤 Start Recording
    </button>
    
    <button onclick="stopRecording()" 
        style="background-color: #f44336; color: white; padding: 15px 30px; font-size: 18px; border: none; border-radius: 5px; margin: 10px; cursor: pointer;">
        ⏹️ Stop Recording
    </button>
    
    <div id="status" style="margin: 20px; font-size: 16px;"></div>
    
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
        document.getElementById('transcript').innerHTML = '';
    };
    
    recognition.onend = function() {
        document.getElementById('status').innerHTML = '⏹️ Stopped';
        document.getElementById('status').style.color = '#666';
        
        // Send the transcript to Streamlit
        if (finalTranscript) {
            // Use Streamlit's setComponentValue
            Streamlit.setComponentValue(finalTranscript.trim());
        }
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
    };
    
    recognition.onerror = function(event) {
        document.getElementById('status').innerHTML = 'Error: ' + event.error;
        document.getElementById('status').style.color = '#f44336';
    };
} else {
    document.getElementById('status').innerHTML = '❌ Speech recognition not supported. Please use Chrome.';
}

function startRecording() {
    if (recognition) {
        finalTranscript = '';
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
col1, col2 = st.columns(2)

with col1:
    st.subheader="🎙️ Recording"
    # Get the transcript from the component
    result = components.html(html_code, height=450)
    
    # Update session state if we got a result
    if result:
        st.session_state.transcript = result

with col2:
    st.subheader="📝 Your Text"
    
    if st.session_state.transcript:
        # Show the transcript
        edited_text = st.text_area(
            "Edit if needed:",
            st.session_state.transcript,
            height=200
        )
        
        # Buttons
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("💾 Save", use_container_width=True):
                st.session_state.history.append(edited_text)
                st.success("✅ Saved to history!")
        
        with col_b:
            st.download_button(
                label="📥 Download",
                data=edited_text,
                file_name="transcript.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col_c:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.transcript = ""
                st.rerun()
    else:
        st.info("👆 Click 'Start Recording', speak, then click 'Stop Recording'")

# History section
st.markdown("---")
st.subheader="📜 History"

if st.session_state.history:
    for i, text in enumerate(reversed(st.session_state.history[-10:])):
        with st.expander(f"Recording {len(st.session_state.history) - i} - {text[:50]}..."):
            st.write(text)
            if st.button("Load", key=f"load_{i}"):
                st.session_state.transcript = text
                st.rerun()
else:
    st.info("No saved transcripts yet")

# Sidebar
with st.sidebar:
    st.header="ℹ️ Instructions"
    st.markdown("""
    1. Click **Start Recording**
    2. Allow microphone access
    3. Speak clearly
    4. Click **Stop Recording**
    5. Your text appears on the right
    6. Edit, save, or download
    """)
    
    st.markdown("---")
    st.metric("Total Recordings", len(st.session_state.history))
    
    if st.button("Clear All History"):
        st.session_state.history = []
        st.rerun()
