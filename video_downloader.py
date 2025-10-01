import streamlit as st
from pytubefix import YouTube, Search, exceptions
from pytubefix.cli import on_progress
from streamlit_elements import media, elements
import tempfile
import os

st.set_page_config(layout="wide")

def middle():
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        pass
    with col2:
        main()
    with col3:
        pass

def show_info(url):
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        st.text(yt.title)
    except exceptions.LoginRequired:
        st.error("This video requires login to view.")

def download(url, progress_bar, progress_text):
    try:
        yt = YouTube(url, on_progress_callback=lambda stream, chunk, bytes_remaining: custom_on_progress(stream, chunk, bytes_remaining, progress_bar, progress_text))
        ys = yt.streams.get_highest_resolution()
        
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        
        # Download the video to the temporary directory
        file_path = ys.download(output_path=temp_dir)
        
        # Provide a download button
        with open(file_path, "rb") as file:
            st.download_button(label="Download Video", data=file, file_name=f"{yt.title}.mp4", mime="video/mp4")
        
        st.success("Download Complete!")
    except exceptions.LoginRequired:
        st.error("This video requires login to download.")

# Custom progress callback for Streamlit
def custom_on_progress(stream, chunk, bytes_remaining, progress_bar, progress_text):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage = bytes_downloaded / total_size * 100

    # Update progress bar and progress text
    progress_bar.progress(min(percentage / 100, 1.0))  # Ensure it's within 0-1
    progress_text.text(f"Progress: {percentage:.2f}%")

def player(a):
    with elements("media_player"):
        media.Player(a, controls=True)

def main():
    st.header("YouTube Downloader")
    with st.container(border=True):
        a = st.text_input("Input a URL")
        if a:
            show_info(a)
            player(a)
            if st.button("Download"):
                st.balloons()
                # Create progress bar and text element
                progress_bar = st.progress(0)
                progress_text = st.empty()
                download(a, progress_bar, progress_text)

pages = st.sidebar.selectbox("select a value", ["Download", "Search"])

def search(b):
    result = Search(b)
    for video in result.videos:
        try:
            st.text(f'Title: {video.title}')
            button = st.button(video.watch_url)
            if button:
                player(button)
            
            st.text(f'Duration: {video.length} seg')
            print('---')
        except exceptions.LoginRequired:
            st.error("This video requires login to view.")

if pages == "Download":
    middle()
if pages == "Search":
    st.session_state.a = st.text_input("Here you can search videos")
    search(st.session_state.a)
