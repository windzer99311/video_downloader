import os
import streamlit as st
from pytubefix import YouTube
import requests
link=st.text_input("Enter Your Url")
if link:
    yt=YouTube(link)
    stream=yt.streams.filter(res='360p').first()
    stream_url=stream.url
    response=requests.get(stream_url)
    with open("test.mp4","wb") as f:
        print(response.content)
        f.write(response.content)
    st.success("Downloaded")
    with open("test.mp4","rb") as f:
        st.download_button(
            label="⬇️ Download Video",
            data=f,
            file_name="test.mp4",
            mime="video/mp4"
        )
    os.remove("test.mp4")
