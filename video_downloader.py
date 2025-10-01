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
    st.text_area(f"{response.content}")
    os.remove("test.mp4")
