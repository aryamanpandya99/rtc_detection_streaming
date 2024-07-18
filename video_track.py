"""
This module provides a video track for the webcam, enabling
video streaming to the peer connection.
"""

import cv2
from aiortc import VideoStreamTrack
from av import VideoFrame


class WebCamTrack(VideoStreamTrack):
    """
    Extends aiortc's VideoStreamTrack to provide a track that streams live
    webcam content
    """

    def __init__(self, device_index=0):
        super().__init__()
        self.cap = cv2.VideoCapture(device_index)

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to read frame from webcam")

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        return video_frame

    def stop(self):
        self.cap.release()
        super().stop()
