import streamlit as st
from audio_recorder_streamlit import audio_recorder
import tempfile
import os

st.set_page_config(page_title="Test Recorder", layout="wide")

st.title("Recorder Test")

audio_bytes = audio_recorder(
    text="Click to record",
    recording_color="#ff0000",
    neutral_color="#6c757d",
    icon_size="3x"
)

if audio_bytes:
    st.success(f"✅ Audio received! Size = {len(audio_bytes)} bytes")
    st.audio(audio_bytes, format="audio/wav")
else:
    st.info("Click the microphone to start recording")

st.write("---")
st.write("If you don't see the red recording animation when you click, the component is broken.")
