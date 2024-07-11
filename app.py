import av
import numpy as np
import pydub
import streamlit as st
from streamlit_webrtc import WebRtcMode, webrtc_streamer
from datetime import datetime
from sqlalchemy.sql import text

conn = st.connection('pets_db', type='sql', ttl=0)

def store(db):
    with conn.session as s:
        s.execute(text("CREATE TABLE IF NOT EXISTS pet_owners (time TEXT, db INT);"))
        s.execute(text("DELETE FROM pet_owners;"))
        s.execute(
            text("INSERT INTO pet_owners (time, db) VALUES (:time, :db);"),
            params=dict(time=datetime.now().strftime("%H:%M:%S"), db=db)
        )
        s.commit()

def process_audio(frame: av.AudioFrame) -> av.AudioFrame:
    raw_samples = frame.to_ndarray()
    sound = pydub.AudioSegment(
        data=raw_samples.tobytes(),
        sample_width=frame.format.bytes,
        frame_rate=frame.sample_rate,
        channels=len(frame.layout.channels),
    )

    sound = sound.apply_gain(10)

    # Ref: https://github.com/jiaaro/pydub/blob/master/API.markdown#audiosegmentget_array_of_samples  # noqa
    channel_sounds = sound.split_to_mono()
    channel_samples = [s.get_array_of_samples() for s in channel_sounds]
    new_samples: np.ndarray = np.array(channel_samples).T
    new_samples = new_samples.reshape(raw_samples.shape)

    new_frame = av.AudioFrame.from_ndarray(new_samples, layout=frame.layout.name)
    new_frame.sample_rate = frame.sample_rate
    db =  int(20 * np.log10(np.sqrt(np.mean(abs(raw_samples))**2)))
    store(db)
    return new_frame

webrtc_streamer(
    key="audio-filter",
    mode=WebRtcMode.SENDRECV,
    audio_frame_callback=process_audio,
    async_processing=True,
)