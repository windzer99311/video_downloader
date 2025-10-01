import os
import streamlit as st
from pytubefix import YouTube

st.title("🎥 YouTube Downloader")

link = st.text_input("Enter YouTube URL")

if link:
    yt = YouTube(link)
    stream = yt.streams.filter(res="360p", progressive=True).first()  # progressive ensures full mp4
    if stream is None:
        st.error("No 360p progressive stream available.")
    else:
        temp_file = "test.mp4"
        stream.download(filename=temp_file)

        st.success("✅ Download complete!")

        with open(temp_file, "rb") as f:
            st.download_button(
                label="⬇️ Download Video",
                data=f,
                file_name="video.mp4",
                mime="video/mp4"
            )

        os.remove(temp_file)
