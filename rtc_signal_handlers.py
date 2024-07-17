"""
This module contains the signaling handlers for the RTC connection.
"""

from aiortc import RTCIceCandidate, RTCSessionDescription
from aiortc.contrib.signaling import BYE


async def handle_signaling(signaling, pc):
    """
    Handle signaling messages and handle them accordingly.

    Args:
        signaling (Signaling): The signaling object used for communication.
        pc (RTCPeerConnection): The RTCPeerConnection object.

    Returns:
        None

    Raises:
        None
    """
    obj = await signaling.receive()

    if isinstance(obj, RTCSessionDescription):
        await pc.setRemoteDescription(obj)

        if obj.type == "offer":
            # send answer
            await pc.setLocalDescription(await pc.createAnswer())
            await signaling.send(pc.localDescription)

    elif isinstance(obj, RTCIceCandidate):
        await pc.addIceCandidate(obj)
    elif obj is BYE:
        print("Exiting")
        return -1


async def consume_signaling(pc, signaling, limit=None):
    """
    Consume signaling messages and handle them accordingly.

    Args:
        pc (RTCPeerConnection): The RTCPeerConnection object.
        signaling (Signaling): The signaling object used for communication.

    Returns:
        None

    Raises:
        None
    """
    if limit is None:
        while True:
            resp = await handle_signaling(signaling, pc)
            if resp == -1:
                break
    else:
        for _ in range(limit):
            resp = await handle_signaling(signaling, pc)
            if resp == -1:
                break
