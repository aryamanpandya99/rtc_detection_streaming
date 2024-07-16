"""
This module implements the client-side functionality for real-time object detection and
communication using WebRTC.

The client connects to a signaling server, sets up event handlers, and processes video 
frames for object detection using a pre-trained YOLOv5 model. The detected coordinates
are shared with the server for further processing.

Author: Aryaman Pandya
"""

import argparse
import asyncio
import multiprocessing as mp
from multiprocessing import freeze_support

import numpy as np
import torch
import cv2

from aiortc import RTCPeerConnection
from aiortc.contrib.signaling import add_signaling_arguments, create_signaling

from rtc_signal_handlers import consume_signaling

model = torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True)

def face_detection(frame: np.ndarray) -> np.ndarray:
    """
    Perform face detection on the input frame and return the frame with detections drawn.

    Parameters:
    frame (np.ndarray): The input image frame.

    Returns:
    np.ndarray: The frame with detections drawn.
    """
    global model
    
    if torch.cuda.is_available():
        model.to("cuda")
    
    results = model(frame)
    
    for detection in results.xyxy[0]:  # xyxy format for bounding boxes
        x1, y1, x2, y2, conf, cls = detection[:6]
        label = f"{results.names[int(cls)]} {conf:.2f}"
        
        # Draw the bounding box
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        
        # Put the label text above the bounding box
        cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return frame


async def run_client(pc, signaling, frame_queue):
    """
    Connects to the signaling server, sets up event handlers, and consumes signaling.

    Args:
        pc (RTCPeerConnection): The PeerConnection object.
        signaling (Signaling): The signaling object.
        frame_queue (Queue): Queue for received frames.
        detection_queue (Queue): Queue for detected frames.

    Returns:
        None
    """
    await signaling.connect()

    @pc.on("track")
    def on_track(track):
        if track.kind == "video":
            asyncio.ensure_future(display_frames(track, frame_queue))
        else: 
            raise ValueError(f"Unsupported track kind: {track.kind}")

    await consume_signaling(pc, signaling)


async def display_frames(track, frame_queue):
    """
    Display frames received from a video track and put frames into a queue.

    Args:
        track (VideoTrack): The video track to receive frames from.
        frame_queue (Queue): The queue to put the received frames into.

    Returns:
        None
    """
    while True:
        try:
            frame = await track.recv()
            img = frame.to_ndarray(format="bgr24")
            frame_queue.put(img)
            cv2.imshow("Received Video", img)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        except MediaStreamError:
            print("MediaStreamError: The media stream was interrupted or is unavailable.")
            continue


def update_detection(frame_queue: mp.Queue, detection_queue: mp.Queue):
    """
    Process frames from the frame_queue for face detection and put results into detection_queue.

    Args:
        frame_queue (Queue): Queue for received frames.
        detection_queue (Queue): Queue for detected frames.

    Returns:
        None
    """
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            detected_frame = face_detection(frame)
            detection_queue.put(detected_frame)


async def display_detections(detection_queue: mp.Queue):
    """
    Display frames with detections from the detection_queue.

    Args:
        detection_queue (Queue): Queue for detected frames.

    Returns:
        None
    """
    while True:
        if not detection_queue.empty():
            detected_frame = detection_queue.get()
            cv2.imshow("Detections", detected_frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        await asyncio.sleep(0.01)  # small sleep to prevent high CPU usage


def main():
    """
    Entry point of the program.

    Args:
        None

    Returns:
        None
    
    Raises:
        RuntimeError: If the frame cannot be read from the webcam.
        KeyboardInterrupt: If the program is interrupted by the user.
    """
    parser = argparse.ArgumentParser(description="Data channels ping/pong")
    add_signaling_arguments(parser)
    args = parser.parse_args()

    signaling = create_signaling(args)
    pc = RTCPeerConnection()

    freeze_support()
    frame_queue = mp.Queue()
    detection_queue = mp.Queue()

    p = mp.Process(target=update_detection, args=(frame_queue, detection_queue))
    p.start()

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(asyncio.gather(
            run_client(pc, signaling, frame_queue),
            display_detections(detection_queue)
        ))
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(pc.close())
        loop.run_until_complete(signaling.close())
        p.terminate()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()