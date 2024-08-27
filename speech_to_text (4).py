import os
import requests
import streamlit as st
from io import BytesIO
from audiorecorder import audiorecorder
from openai import OpenAI
from dotenv import load_dotenv
from pydub import AudioSegment
import imageio_ffmpeg as ffmpeg
from streamlit_autorefresh import st_autorefresh

# This will refresh the app every 14 minutes
st_autorefresh(interval=14 * 60 * 1000, key="refresh")

# Set the ffmpeg path for pydub
AudioSegment.ffmpeg = ffmpeg.get_ffmpeg_exe()

# Load environment variables
load_dotenv()

# Set up API key
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

st.subheader("Choose an option to provide audio:")
audio_input_method = st.selectbox(
    "Audio Input Method",
    ("Record Audio", "Upload Audio"),
    index=None,
    placeholder="Select the input method...",
)

# Define the max file size in bytes (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

if audio_input_method == "Upload Audio":
    audio_file = st.file_uploader("Upload Audio (max. 5MB)", type=["wav", "mp3", "m4a"])
    if audio_file is not None:
        if audio_file.size > MAX_FILE_SIZE:
            st.error("File size exceeds 5MB. Please upload a smaller file.")
        else:
            temp_audio_path = "temp_audio_file.wav"
            with open(temp_audio_path, "wb") as f:
                f.write(audio_file.getbuffer())

            st.write("Transcribing...")
            with open(temp_audio_path, "rb") as audio:
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    response_format="text"
                )
            transcript = response
            st.write("Transcription:")
            st.write(transcript)

            txt_data = transcript.encode('utf-8')
            st.download_button(
                label="Download Transcription",
                data=txt_data,
                file_name='transcription.txt',
                mime='text/plain',
            )

            os.remove(temp_audio_path)

elif audio_input_method == "Record Audio":
    audio = audiorecorder("Click to record", "Stop")
    if len(audio) > 0:
        st.audio(audio.export().read())

        if st.button("Submit"):
            st.write("Transcribing...")

            audio_buffer = BytesIO(audio.export().read())
            
            if audio_buffer.getbuffer().nbytes > MAX_FILE_SIZE:
                st.error("Recorded file size exceeds 5MB. Please record a shorter audio.")
            else:
                response = requests.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}"},
                    files={"file": ("record.wav", audio_buffer, "audio/wav")},
                    data={"model": "whisper-1", "response_format": "text"}
                )

                if response.status_code == 200:
                    transcript = response.text
                    st.write("Transcription:")
                    st.write(transcript)

                    txt_data = transcript.encode('utf-8')
                    st.download_button(
                        label="Download Your Vocal Note",
                        data=txt_data,
                        file_name='transcription.txt',
                        mime='text/plain',
                    )
                else:
                    st.write("Transcription failed. Please try again.")


# Custom CSS for the sidebar and main container
st.markdown("""
    <style>
        h1{
            color: #000;
            font-size: 28px;
            margin-bottom: 20px;
        }
        button{
            background: #0025B8 !important;
            color: #fff !important;
            border: none !important;
            display: flex !important;
            width: fit-content !important;
            margin: auto !important;
        }
        button p{
            color: #fff !important;
        }
        p{  
            color: #000;
            font-size: 16px !important;
        }
        ul li a{
            padding: 10px 12px;
        }
        #blog-generator{
            text-align: center;
        }
        .stMarkdown{
            text-align: justify;
        }
        
        .stApp {
            background-color: #F4F4FF;
            padding: 20px;
        }
            
        .eczjsme18{
            background: #fff;
        } 
     
        .block-container {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
            margin-top: 20px;
            margin-bottom: 10px;
            width: 95%;  /* Changed to 95% of the screen width */
            max-width: 95%; /* Ensures the block container doesn’t exceed 95% of the screen width */
            margin-left: auto;  /* Center-aligns the container */
            margin-right: auto; /* Center-aligns the container */
        }
        .css-1y6r8k8 {
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
        }
        .st-ae {
            background: #F4F4FF;
            border: none;
        }
        .st-ae:focus{
            outline: none !important;
        }
        .st-emotion-cache-5k5r22:active{
            color: red !important;
        }

        /* Apply background color to the file uploader widget */
        .stFileUploader {
            background-color: #F4F4FF !important;
            border-radius: 10px !important;
            padding: 10px !important;
            box-shadow: 0px 0px 15px rgba(0, 0, 0, 0) !important;
        }

        /* Ensure the input inside the file uploader matches the background */
        .stFileUploader input[type="file"] {
            background-color: #F4F4FF !important;
            color: #000 !important;
        }
    </style>
    """, unsafe_allow_html=True)
















