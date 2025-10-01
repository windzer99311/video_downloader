import io
import streamlit as st
from pytubefix import YouTube

link = st.text_input("Enter YouTube URL")

if link:
    yt = YouTube(link)
    stream = yt.streams.filter(res="360p", progressive=True).first()

    if stream:
        buffer = io.BytesIO()
        stream.stream_to_buffer(buffer)
        buffer.seek(0)

        st.download_button(
            label="⬇️ Download Video",
            data=buffer,
            file_name="video.mp4",
            mime="video/mp4"
        )
    else:
        st.error("No 360p progressive stream available")
