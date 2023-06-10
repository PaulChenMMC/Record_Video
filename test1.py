import uuid
from pathlib import Path
import av
import cv2
import streamlit as st
from aiortc.contrib.media import MediaRecorder
from streamlit_webrtc import WebRtcMode, webrtc_streamer
from turn import get_ice_servers
from moviepy.editor import VideoFileClip
import datetime

#現在YYYYMMDD_HHMMSS
def get_current_datetime():
    now = datetime.datetime.now()
    formatted_datetime = now.strftime("%Y%m%d_%H%M%S")
    return formatted_datetime

#web 顯示即時畫面
def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
    img = frame.to_ndarray(format="bgr24")
    return av.VideoFrame.from_ndarray(img, format="bgr24")

#產生record資料夾
RECORD_DIR = Path("./records")
RECORD_DIR.mkdir(exist_ok=True)


def app():
    if "prefix" not in st.session_state:
        st.session_state["prefix"] = str(uuid.uuid4())
    prefix = st.session_state["prefix"]
    in_file = RECORD_DIR / f"{prefix}_input.mp4"
    out_file=RECORD_DIR / f"{get_current_datetime()}_input.mp4"

    def in_recorder_factory() -> MediaRecorder:
        return MediaRecorder(
            str(in_file), format="mp4"
        )  # HLS does not work. See https://github.com/aiortc/aiortc/issues/331

    def in_recorder_factory() -> MediaRecorder:
        return MediaRecorder(str(in_file), format="mp4")

    webrtc_streamer(
        key="record",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={"iceServers": get_ice_servers()},
        media_stream_constraints={
            "video": True,
            "audio": True,
        },
        video_frame_callback=video_frame_callback,
        in_recorder_factory=in_recorder_factory,
    )

    if in_file.exists():
        clip = VideoFileClip(str(in_file))
        modified_clip = clip.resize((1920, 1080)).set_fps(60)
        modified_clip.write_videofile(str(out_file), codec="libx264", audio_codec="aac")
        
        with out_file.open("rb") as f:
            st.download_button(
                "Download recorded video", f, "input.mp4"
            )

if __name__ == "__main__":
    app()
