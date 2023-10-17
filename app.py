import streamlit as st
import moviepy.editor as mp
import speech_recognition as sr
import requests
import os
import re 

def find_video(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".mp4") or filename.endswith(".avi"):  # Add or modify the file extensions as needed
            print(f"Name of file = {filename}")

find_video('.')  # Searches the current directory

def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def download_video(url):
    local_filename = url.split('/')[-1]
    local_filename = sanitize_filename(local_filename)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

def extract_audio(video_file):
    video = mp.VideoFileClip(video_file)
    audio = video.audio
    audio_file = "audio.wav"
    audio.write_audiofile(audio_file)
    return audio_file

def transcribe_audio(audio_file):
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = r.record(source)
    try:
        text = r.recognize_google(audio_data)
        return text
    except sr.RequestError as e:
        st.error(f"Could not request results; {e}")
    except sr.UnknownValueError:
        st.error("Google Speech Recognition could not understand audio")

def main():
    st.title('SummaLearn')
    st.write('Provide a link to a video to extract and transcribe the audio.')

    video_url = st.text_input("Enter video URL:")

    if video_url:
        with st.spinner('Downloading video...'):
            video_file = download_video(video_url)

        with st.spinner('Extracting audio...'):
            audio_file = extract_audio(video_file)

        with st.spinner('Transcribing audio...'):
            transcription = transcribe_audio(audio_file)

        if transcription:
            st.write('Transcription:')
            st.write(transcription)
        else:
            st.error('Transcription failed.')

        # Clean up by removing downloaded video and audio files
        os.remove(video_file)
        os.remove(audio_file)

if __name__ == "__main__":
    main()
