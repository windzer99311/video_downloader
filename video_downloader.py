import os
import subprocess
import streamlit as st
from pytubefix import YouTube

# Filenames
video_file = "video.mp4"
audio_file = "audio.mp4"
output_file = "output.mp4"

def merge(video_data, audio_data, output_path):
    st.info("Merging video and audio with FFmpeg...")
    cmd = [
        "ffmpeg",
        "-y",               # overwrite if exists
        "-i", video_data,
        "-i", audio_data,
        "-c", "copy",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        st.error("❌ FFmpeg failed!")
        st.code(result.stderr)
        return False
    return True


# Streamlit UI
st.title("🎬 YouTube Downloader with Merge")

url = st.text_input("Enter YouTube Video URL:")

if st.button("Process Video"):
    if not url:
        st.warning("⚠️ Please enter a URL first.")
    else:
        try:
            yt = YouTube(url)
            st.success(f"📌 Title: {yt.title}")

            # Pick highest resolution video (no audio)
            video_stream = yt.streams.filter(only_video=True, file_extension="mp4") \
                                      .order_by("resolution").desc().first()

            # Pick best audio
            audio_stream = yt.streams.filter(only_audio=True, file_extension="mp4") \
                                      .order_by("abr").desc().first()

            if not video_stream or not audio_stream:
                st.error("❌ Could not find suitable video/audio streams.")
            else:
                st.info(f"⬇️ Downloading video ({video_stream.resolution})...")
                video_stream.download(filename=video_file)

                st.info("⬇️ Downloading audio...")
                audio_stream.download(filename=audio_file)

                if merge(video_file, audio_file, output_file):
                    st.success("✅ Video Processed Successfully!")
                    st.video(output_file)

                    # Offer download button
                    with open(output_file, "rb") as f:
                        st.download_button(
                            label="📥 Download Final Video",
                            data=f,
                            file_name=f"{yt.title}.mp4",
                            mime="video/mp4"
                        )

        except Exception as e:
            st.error(f"❌ Error: {e}")
