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

# Simple speech recognition HTML
html = """
<div style="text-align: center; padding: 20px;">
    <button onclick="startRec()" style="background: #4CAF50; color: white; padding: 15px 30px; font-size: 18px; border: none; border-radius: 5px; margin: 10px; cursor: pointer;">
        🎤 Start Recording
    </button>
    <button onclick="stopRec()" style="background: #f44336; color: white; padding: 15px 30px; font-size: 18px; border: none; border-radius: 5px; margin: 10px; cursor: pointer;">
        ⏹️ Stop Recording
    </button>
    <p id="status" style="font-size: 16px; margin: 10px;"></p>
    <div id="output" style="border: 2px solid #ddd; border-radius: 10px; padding: 20px; min-height: 150px; background: #f9f9f9; font-size: 18px; text-align: left;"></div>
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
        document.getElementById('output').innerHTML = 
            '<strong>Final:</strong> ' + finalTranscript + '<br>' +
            '<strong>Interim:</strong> ' + interimTranscript;
        
        // Send to Streamlit as a string
        if (finalTranscript) {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: String(finalTranscript)
            }, '*');
        }
    };
    
    recognition.onerror = function(event) {
        document.getElementById('status').innerHTML = 'Error: ' + event.error;
        document.getElementById('status').style.color = '#f44336';
    };
} else {
    document.getElementById('status').innerHTML = '❌ Speech recognition not supported. Please use Chrome.';
}

function startRec() {
    if (recognition) {
        finalTranscript = '';
        document.getElementById('output').innerHTML = '';
        recognition.start();
    }
}

function stopRec() {
    if (recognition) {
        recognition.stop();
    }
}
</script>
"""

# Layout
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader="🎙️ Recording"
    # Get transcript from component
    result = components.html(html, height=400)
    
    # Convert to string if we got a result
    if result is not None:
        # Ensure it's a string
        st.session_state.transcript = str(result)
        st.success("✅ Speech captured!")

with col2:
    st.subheader="📝 Current Text"
    
    # Display current transcript
    if st.session_state.transcript:
        # Text area for display/editing
        edited_text = st.text_area(
            "Edit if needed:",
            st.session_state.transcript,
            height=150,
            key="edit_area"
        )
        
        # Buttons
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("💾 Save", use_container_width=True):
                st.session_state.history.append({
                    "text": edited_text,
                    "time": "Just now"
                })
                st.success("Saved!")
        
        with col_b:
            # Download button - using edited_text directly
            st.download_button(
                label="📥 Download",
                data=edited_text,  # This is now definitely a string
                file_name="transcript.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col_c:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.transcript = ""
                st.rerun()
    else:
        st.info("Click 'Start Recording' and speak")
        st.session_state.transcript = ""

# History section
st.markdown("---")
st.subheader="📜 History"

if st.session_state.history:
    for i, item in enumerate(reversed(st.session_state.history[-10:])):
        with st.expander(f"{item['time']} - {item['text'][:50]}..."):
            st.write(item['text'])
            if st.button("Load", key=f"load_{i}"):
                st.session_state.transcript = item['text']
                st.rerun()
else:
    st.info("No saved transcripts yet")

# Sidebar
with st.sidebar:
    st.header="ℹ️ How to use"
    st.markdown("""
    1. Click **Start Recording**
    2. Allow microphone access
    3. Speak clearly
    4. Click **Stop Recording**
    5. Edit text if needed
    6. Save or download
    """)
    
    st.markdown("---")
    st.metric("Total Recordings", len(st.session_state.history))
