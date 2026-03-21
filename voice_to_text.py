import streamlit as st
from audio_recorder_streamlit import audio_recorder

st.set_page_config(page_title="Simple Recorder Test", layout="wide")

st.title("Simple Recorder Test")

audio_bytes = audio_recorder(
    text="Click the microphone to record",
    recording_color="#ff0000",
    neutral_color="#666666",
    icon_size="5x",
    key="recorder_v1"   # Important
)

if audio_bytes:
    st.success(f"✅ Recording successful! Audio size: {len(audio_bytes)} bytes")
    st.audio(audio_bytes, format="audio/wav")
else:
    st.info("No recording yet. Click the microphone above.")
