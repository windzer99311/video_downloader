import os
import requests
import streamlit as st
from pytubefix import YouTube

link = st.text_input("Enter YouTube URL")

if link:
    yt = YouTube(link)
    stream = yt.streams.filter(res="360p").first()
    stream_url = stream.url

    # Get total size
    head = requests.head(stream_url)
    total_size = int(head.headers.get("content-length", 0))

    temp_file = "test.mp4"
    chunk_size = 1024 * 1024  # 1 MB

    with open(temp_file, "wb") as f:
        for start in range(0, total_size, chunk_size):
            end = min(start + chunk_size - 1, total_size - 1)
            headers = {"Range": f"bytes={start}-{end}"}
            r = requests.get(stream_url, headers=headers)
            f.write(r.content)

    st.success("Downloaded ✅")

    with open(temp_file, "rb") as fs:
        st.download_button(
            label="⬇️ Download Video",
            data=fs,
            file_name="test.mp4",
            mime="video/mp4"
        )

    os.remove(temp_file)
