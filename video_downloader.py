import streamlit as st
from pytube import YouTube
import requests
from io import BytesIO

def fetch_thumbnail(video_url):
    try:
        yt = YouTube(video_url)
        thumbnail_url = yt.thumbnail_url
        return thumbnail_url, yt.title
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None, None

def download_thumbnail(thumbnail_url):
    try:
        response = requests.get(thumbnail_url)
        response.raise_for_status()
        return BytesIO(response.content)
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching the thumbnail: {e}")
        return None

# Streamlit UI
st.title("YouTube Thumbnail Downloader")
st.write("Enter a YouTube video URL to download its thumbnail.")

video_url = st.text_input("YouTube Video URL", "")

if st.button("Fetch Thumbnail"):
    if video_url.strip():
        thumbnail_url, video_title = fetch_thumbnail(video_url.strip())
        if thumbnail_url:
            st.success(f"Thumbnail fetched for: {video_title}")
            st.image(thumbnail_url, caption=video_title, use_column_width=True)

            if st.button("Download Thumbnail"):
                thumbnail_file = download_thumbnail(thumbnail_url)
                if thumbnail_file:
                    st.download_button(
                        label="Download Thumbnail",
                        data=thumbnail_file,
                        file_name=f"{video_title}_thumbnail.jpg",
                        mime="image/jpeg",
                    )
    else:
        st.warning("Please enter a valid YouTube video URL.")
