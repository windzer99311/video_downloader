import os
import streamlit as st
from pytubefix import YouTube
import requests
link=st.text_input("Enter Your Url")
if link:
    yt=YouTube(link)
    stream=yt.streams.filter(res='360p').first()
    stream_url=r"https://rr8---sn-ci5gup-25us.googlevideo.com/videoplayback?expire=1759356001&ei=AVDdaL-2JfCD9fwP0JPy4Ak&ip=2401%3A4900%3A3b1c%3Ae14%3A501a%3A5fd2%3Af013%3Abaff&id=o-AJW4b_LW-3uPfLk-9UyoMSo3LjcfVA7NKqRiFvieh0RA&itag=18&source=youtube&requiressl=yes&xpc=EgVo2aDSNQ%3D%3D&met=1759334401%2C&mh=lv&mm=31%2C29&mn=sn-ci5gup-25us%2Csn-ci5gup-cvhk&ms=au%2Crdu&mv=m&mvi=8&pl=48&rms=au%2Cau&initcwndbps=358750&bui=ATw7iSXTuOhZb6WtocZKNoylB6jpyDWlxFollnbdua11REOxOq6DmuYtDnyixxc2YTGUce2SBxj3aPWe&spc=hcYD5bqZlA4MPEasI_0LsB6F21A1ntNpizqvwQ9bAlxhwFuCGIYruQeIqB0&vprv=1&svpuc=1&mime=video%2Fmp4&rqh=1&gir=yes&clen=4703329&ratebypass=yes&dur=54.102&lmt=1733490624624341&mt=1759333842&fvip=6&fexp=51552689%2C51565115%2C51565681%2C51580968&c=ANDROID_VR&txp=6309224&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cxpc%2Cbui%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Crqh%2Cgir%2Cclen%2Cratebypass%2Cdur%2Clmt&sig=AJfQdSswRQIgVB47E6Yh1fJ0s2QljkVzeLQH6_yluH3cciMPbX1bWdQCIQCIfqalYpveYUpjPHidMc2_lun7-M8un5-bGYraUv4ftA%3D%3D&lsparams=met%2Cmh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Crms%2Cinitcwndbps&lsig=APaTxxMwRgIhALqJYjbDbL0Ct9GQklD3W_PgVeFJjkVaue_nx0la8s4sAiEAn7MYAeJ0usBipINsPoHukxixEhrd32wtR7qEWNSBvIw%3D"
    print(stream_url)
    response=requests.get(stream_url)
    st.write(len(response.content))
    with open("test.mp4","wb") as f:
        f.write(response.content)
    st.success("Downloaded")
    with open("test.mp4","rb") as fs:
        st.download_button(
            label="⬇️ Download Video",
            data=fs,
            file_name="test.mp4",
            mime="video/mp4"
        )

