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
import ctypes
import multiprocessing as mp
from multiprocessing import freeze_support

import numpy as np
from PIL import Image
import torch
import cv2

from aiortc import RTCPeerConnection
from aiortc.contrib.signaling import add_signaling_arguments, create_signaling

from rtc_signal_handlers import consume_signaling

def face_detection(frame: np.ndarray) -> tuple:
    """
    """
    model = torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True)
    if torch.cuda.is_available():
        model.to("cuda")
    
    results = model(frame)
    print(results)
    return (-1, -1)


class Coordinates(ctypes.Structure):
    """
    Coordinates ctype structure
    """

    _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float)]



async def run_client(pc, signaling, queue, coordinates):
    """
    Connects to the signaling server, sets up event handlers, and consumes signaling.

    Args:
        pc (obj): The PC object.
        signaling (obj): The signaling object.
        queue (obj): The queue object.
        coordinates (obj): The coordinates object.

    Returns:
        None
    """
    await signaling.connect()

    @pc.on("track")
    def on_track(track):
        if track.kind == "video":
            asyncio.ensure_future(display_frames(track, queue))
            # asyncio.ensure_future(print_coords(coordinates))
        else: 
            raise ValueError(f"Unsupported track kind: {track.kind}")

    await consume_signaling(pc, signaling)


async def display_frames(track, queue):
    """
    Display frames received from a video track.

    Args:
        track (VideoTrack): The video track to receive frames from.
        queue (Queue): The queue to put the received frames into.

    Returns:
        None
    """
    while True:
        frame = await track.recv()
        img = frame.to_ndarray(format="bgr24")
        queue.put(img)
        cv2.imshow("Received Video", img)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


async def print_coords(coords, channel):
    """Sends the coordinates to the specified channel.

    Args:
        coords (Coordinates): The coordinates to be sent.
        channel (Channel): The channel to send the coordinates to.

    Raises:
        None

    Returns:
        None
    """
    while True:
        print(f"x: {coords.x}, y: {coords.y}")


def update_detection(q: mp.Queue, coords):
    """

    """
    while True:
        if q.get() is not None:
            x, y = face_detection(q.get())
            with coords.get_lock():
                coords.x = x
                coords.y = y


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
    loop = asyncio.get_event_loop()
    q = mp.Queue()
    shared_coordinates = mp.Value(Coordinates)  # Shared value for x, y coordinates
    p = mp.Process(target=update_detection, args=(q, shared_coordinates))

    p.start()

    try:
        loop.run_until_complete(run_client(pc, signaling, q, shared_coordinates))
    except KeyboardInterrupt:
        pass

    finally:
        loop.run_until_complete(pc.close())
        loop.run_until_complete(signaling.close())
        p.terminate()


if __name__ == "__main__":
    main()
