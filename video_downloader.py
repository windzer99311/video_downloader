import os, subprocess, requests, time, streamlit as st
from pytubefix import YouTube
from pytubefix.exceptions import RegexMatchError
from math import ceil, floor
from concurrent.futures import ThreadPoolExecutor

video_segment_list, audio_segment_list, Reso_list, Aud_list, vid_resolution, aud_resolution, Reso_check = [], [], [], [], [], [], []
video_file, audio_file, output_file = "Video.mp4", "Audio.mp3", 'Downloaded.mp4'
only_audio = []
total_received, percentage = 0, 0
Resolution_list=[]
Raw_rso_list=[]

def create_throttles(size):
    mb = 1024 * 1024
    if size >= mb:
        if ceil(size / mb) >= 16:
            return 16
        else:
            return ceil(size / mb)
    else:
        return 1

def range_list(file_size, parts, file_type):
    end = 0
    start = 0
    segment_size = floor(file_size / parts)
    for i in range(parts):
        end = end + (segment_size - 1)
        if i != parts - 1:
            if 'Video' in file_type:
                video_segment_list.append((start, end))
            else:
                audio_segment_list.append((start, end))
        else:
            end = file_size
            if 'Video' in file_type:
                video_segment_list.append((start, end))
            else:
                audio_segment_list.append((start, end))
        start = end + 1

def metadata(stream_data, yt):
    thumbnail = yt.thumbnail_url
    title = stream_data.first().title
    views = yt.views
    duration = time.strftime("%H:%M:%S", time.gmtime(yt.length))
    return thumbnail, title, views, duration

def track_progress(data_received, total_length):
    global total_received, percentage
    total_received += len(data_received)
    percentage = round((total_received / total_length) * 100, 2)

def download_chunk(start, stop, data_stream, total_length):
    headers = {"Range": f"bytes={start}-{stop}"}
    response = requests.get(data_stream, headers=headers, stream=True)
    downloaded = response.content
    track_progress(downloaded, total_length)
    return downloaded

def download_segments(data_parts, streaming_url, segment_list, file_type, file_size):
    chunks = []
    with ThreadPoolExecutor(max_workers=4) as executors:
        futures = []
        print("Downloading...")
        for i in range(data_parts):
            start = segment_list[i][0]
            stop = segment_list[i][1]
            futures.append(executors.submit(download_chunk, start, stop, streaming_url, file_size))
        for f in futures:
            chunks.append(f.result())
        with open(f"{file_type}", "wb") as f:
            for chunk in chunks:
                f.write(chunk)

def merge(video_data, audio_data):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_data,
        "-i", audio_data,
        "-c", "copy",  # no re-encoding, just mux
        output_file
    ]
    subprocess.run(cmd, check=True)
    os.remove(video_data)
    os.remove(audio_data)
    st.success("Video Processed Successfully!!")

def store_resolution(raw_list, new_list):
    for i in range(len(raw_list)):
        data = f"{raw_list[i][0]} {str(round(raw_list[i][2] / (1024 * 1024), 2))}  mb"
        new_list.append(data)

def Audio_Ui():
    st.title("🎵 Only Audio Downloader 🎵")
    inp1, inp2 = st.columns(2)
    with inp1:
        link = st.text_input("Enter Url:")
    with inp2:
        st.markdown("<div style='height:25px'></div>", unsafe_allow_html=True)  # tweak height
        check_button = st.button("Check")
    if check_button:
        st.session_state.checked_1 = True
    if st.session_state.get("checked_1", False):
        try:
            yt = YouTube(link)
            streams = yt.streams
            for stream in streams.filter(only_audio=True):
                audio_resolution = stream.abr, stream.itag, stream.filesize, stream.audio_codec
                Aud_list.append(audio_resolution)
            vid_info = metadata(streams, yt)
            store_resolution(Aud_list, aud_resolution)

            col1, col2 = st.columns(2)
            with col1:
                st.image(f"{vid_info[0]}", width=300)
                a = st.selectbox("Audio Resolution", aud_resolution)
                audio_resolution = Aud_list[aud_resolution.index(a)]

            with col2:
                st.subheader(f"Title: {vid_info[1]}")
                st.write(f"Duration:{vid_info[3]}")
                download = st.button("Process")

            if download:
                audio_stream = streams.filter().get_by_itag(audio_resolution[1]).url
                total_size =audio_resolution[2]
                approx_size = round(total_size / (1024 * 1024), 2)
                print(f"File_Size: {approx_size}")
                st.header(f"Size:{approx_size}mb")
                progress_bar = st.progress(0)
                downloading_status = st.empty()

                with ThreadPoolExecutor() as executor:
                    t2 = executor.submit(create_throttles, audio_resolution[2])
                audio_throttles = t2.result()

                with ThreadPoolExecutor() as executor:
                    executor.submit(range_list, audio_resolution[2], audio_throttles, "Audio")

                with ThreadPoolExecutor() as executor:
                    executor.submit(download_segments, audio_throttles, audio_stream, audio_segment_list, audio_file,
                                    total_size)
                    while total_received < total_size:
                        progress_bar.progress(min(int(percentage), 100))
                        downloading_status.text(f"Processed:{percentage}%")
                        time.sleep(0.5)
                        if total_received == total_size:
                            progress_bar.progress(100)
                            downloading_status.text(f"Processed:100%")
                            break

                with open(audio_file, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Audio",
                        data=f,
                        file_name=audio_file,
                        mime="audio/m4a"
                    )
                os.remove(audio_file)
        except RegexMatchError:
            st.error("Please Enter Valid Url!")

def Youtube_Gui():
    st.title("Youtube Video Downloader")
    inp1, inp2 = st.columns(2)
    with inp1:
        link = st.text_input("Enter Video Url:")
    with inp2:
        st.markdown("<div style='height:25px'></div>", unsafe_allow_html=True)  # tweak height
        check_button = st.button("Check")
    if check_button:
        st.session_state.checked_2 = True
    if st.session_state.get("checked_2", False):
        try:
            yt = YouTube(link)
            streams = yt.streams
            for stream in streams.filter(only_video=True):
                video_resolution = stream.resolution, stream.itag, stream.filesize, stream.fps
                if f"{video_resolution[0]}  {str(video_resolution[3])}" not in Reso_check and video_resolution[0]!=None:
                    Reso_list.append(video_resolution)
                    Reso_check.append(f"{video_resolution[0]}  {str(video_resolution[3])}")
            for stream in streams.filter(only_audio=True):
                audio_resolution = stream.abr, stream.itag, stream.filesize, stream.audio_codec
                Aud_list.append(audio_resolution)
            vid_info = metadata(streams, yt)
            store_resolution(Reso_list, vid_resolution)
            store_resolution(Aud_list, aud_resolution)

            col1, col2 = st.columns(2)
            with col1:
                st.image(f"{vid_info[0]}", width=300)
            with col2:
                st.subheader(f"Title: {vid_info[1]}")
                st.write(f"Views: {vid_info[2]}")
                st.write(f"Duration:{vid_info[3]}")
            col3, col4 = st.columns(2)
            with col3:
                v = st.selectbox("Video Resolution", vid_resolution)
                video_resolution = Reso_list[vid_resolution.index(v)]
            with col4:
                a = st.selectbox("Audio Resolution", aud_resolution)
                audio_resolution = Aud_list[aud_resolution.index(a)]
            download = st.button("Process")
            if download:
                video_stream = streams.filter().get_by_itag(video_resolution[1]).url
                audio_stream = streams.filter().get_by_itag(audio_resolution[1]).url
                total_size = video_resolution[2] + audio_resolution[2]
                approx_size = round(total_size / (1024 * 1024), 2)
                print(f"File_Size: {approx_size}")
                st.header(f"Size:{approx_size}mb")
                progress_bar = st.progress(0)
                downloading_status = st.empty()

                with ThreadPoolExecutor() as executor:
                    t1 = executor.submit(create_throttles, video_resolution[2])
                    t2 = executor.submit(create_throttles, audio_resolution[2])

                video_throttles = t1.result()
                audio_throttles = t2.result()

                with ThreadPoolExecutor() as executor:
                    executor.submit(range_list, video_resolution[2], video_throttles, "Video")
                    executor.submit(range_list, audio_resolution[2], audio_throttles, "Audio")

                with ThreadPoolExecutor() as executor:
                    executor.submit(download_segments, video_throttles, video_stream, video_segment_list, video_file,
                                    total_size)
                    executor.submit(download_segments, audio_throttles, audio_stream, audio_segment_list, audio_file,
                                    total_size)
                    while total_received < total_size:
                        progress_bar.progress(min(int(percentage), 100))
                        downloading_status.text(f"Processed:{percentage}%")
                        time.sleep(0.5)
                        if total_received == total_size:
                            progress_bar.progress(100)
                            downloading_status.text(f"Processed:100%")
                            break
                merge(video_file, audio_file)
                with open(output_file, "rb") as f:
                    st.download_button(
                        label="⬇️ Download Video",
                        data=f,
                        file_name=output_file,
                        mime="video/mp4"
                    )
                os.remove(output_file)
        except RegexMatchError:
            st.error("Please Enter Valid Url!")

def segment_resolution(yt):
    streams=yt.streams.filter(only_video=True)
    for stream in streams:
        if stream.resolution not in Resolution_list and stream.resolution!=None:
            Raw_rso_list.append([stream.resolution,stream.itag])
            Resolution_list.append(stream.resolution)


def Section_Download():
    st.title("Youtube Segment Trimmer ✂")
    col1, col2 = st.columns(2)
    with col1:
        url = st.text_input("Enter Video Url:")
    with col2:
        st.markdown("<div style='height:25px'></div>", unsafe_allow_html=True)
        check = st.button("Check")
    if check:
        st.session_state.checked_3 = True
    if st.session_state.get("checked_3", False):
        if url:
            try:
                yt = YouTube(url)
                duration = yt.length
                segment_resolution(yt)
                section_1, section_2 = st.columns(2)
                with section_1:
                    selected_resolution = st.selectbox("Available Resolutions:", Resolution_list)
                with section_2:
                    audio = st.checkbox("With Audio")

                if "Trim" not in st.session_state:
                    st.session_state.Trim = False
                if "start" not in st.session_state:
                    st.session_state.start = 0
                if "play" not in st.session_state:
                    st.session_state.play = False

                # Set Trim state based on URL
                st.session_state.Trim = True if url else False

                # Play video

                st.video(url, autoplay=True, start_time=st.session_state.start)

                # If trimming mode is ON
                if st.session_state.Trim:
                    col3, col4 = st.columns(2)
                    with col3:
                        start = st.number_input("Start Time:", min_value=0, max_value=duration)
                    with col4:
                        end = st.number_input("End Time:", min_value=1, max_value=duration)
                    with col3:
                        s_point = st.button("Start")
                    with col4:
                        e_point = st.button("End")

                    if s_point and start < end:
                        st.session_state.start = start
                        st.session_state.play = True
                        st.rerun()

                    if e_point and start < end:
                        st.session_state.start = end
                        st.session_state.play = True
                        st.rerun()
                    if start >= end:
                        st.info("Trim segment, start time must be less than end time!")
                    process = st.button("Process")
                    if process:
                        stream_1 = yt.streams.get_by_itag(Raw_rso_list[Resolution_list.index(selected_resolution)][1])
                        file_size = stream_1.filesize
                        stream_1_url = stream_1.url
                        if audio:
                            stream_2 = yt.streams.get_lowest_resolution()
                            stream_2_url = stream_2.url
                            file_size += stream_2.filesize

                        progress_bar = st.progress(0)
                        downloading_status = st.empty()

                        with ThreadPoolExecutor() as executor:
                            t1 = executor.submit(create_throttles, file_size)
                            if audio:
                                t2 = executor.submit(create_throttles, file_size)

                        video_throttles = t1.result()
                        if audio:
                            audio_throttles = t2.result()

                        with ThreadPoolExecutor() as executor:
                            executor.submit(range_list, file_size, video_throttles, "Video")
                            if audio:
                                executor.submit(range_list, file_size, audio_throttles, "Audio")

                        with ThreadPoolExecutor() as executor:
                            executor.submit(download_segments, video_throttles,stream_1_url, video_segment_list,
                                            video_file,
                                            file_size)
                            output_file="Video.mp4"
                            if audio:
                                executor.submit(download_segments, audio_throttles, stream_2_url, audio_segment_list,
                                            audio_file,
                                            file_size)
                                output_file="Downloaded.mp4"
                            while total_received < file_size:
                                progress_bar.progress(min(int(percentage), 100))
                                downloading_status.text(f"Processed:{percentage}%")
                                time.sleep(0.5)
                                if total_received == file_size:
                                    progress_bar.progress(100)
                                    downloading_status.text(f"Processed:100%")
                                    break
                        if audio:
                            merge(video_file, audio_file)



                        if start < end and end <= duration:
                            with st.spinner("Trimming video, please wait..."):
                                subprocess.run([
                                    'ffmpeg', '-y', '-ss', f'{start}', '-to', f'{end}', '-i', f'{output_file}',
                                    '-c', 'copy', '-avoid_negative_ts', '1', 'trimmed.mp4'
                                ])
                        else:
                            st.warning("Trim segment, end time must be greater than Video Duration!")
                        trimmed_file = "trimmed.mp4"
                        with open(trimmed_file, "rb") as f:
                            st.download_button(
                                label="⬇️ Download Video",
                                data=f,
                                file_name=trimmed_file,
                                mime="video/mp4"
                            )
                        os.remove(output_file)
                        os.remove(trimmed_file)
            except RegexMatchError:
                st.error("Please enter a valid URL!")
            except TypeError:
                st.error("Please enter a valid URL!")

        else:
            st.warning("Enter URL!")
def main():
    st.sidebar.title("Options:")
    select_option = st.sidebar.selectbox("Youtube_Options:", ["▶️ Video Download", "⬇️ Only Audio","✂ Segment Download"])
    st.session_state["select_option"] = select_option
    if st.session_state.select_option == "▶️ Video Download":
        st.session_state.checked_1 = False
        st.session_state.checked_3 = False
        Youtube_Gui()
    if st.session_state["select_option"] == "⬇️ Only Audio":
        st.session_state.checked_2 = False
        st.session_state.checked_3 = False
        Audio_Ui()
    if st.session_state["select_option"] == "✂ Segment Download":
        st.session_state.checked_2 = False
        st.session_state.checked_1 = False
        Section_Download()

if __name__ == "__main__":
    main()
