import os
import streamlit as st
from pytubefix import YouTube

link = st.text_input("Enter Your Url")

if link:
    yt = YouTube(link)
    stream = yt.streams.filter(res='360p', progressive=True).first()  # progressive ensures video+audio together
    
    if stream:
        file_name = "test.mp4"
        stream.download(filename=file_name)  # pytubefix handles the actual download properly

        st.success("Downloaded")

        with open(file_name, "rb") as f:
            st.download_button(
                label="⬇️ Download Video",
                data=f,
                file_name=file_name,
                mime="video/mp4"
            )
    else:
        st.error("No 360p progressive stream available.")
