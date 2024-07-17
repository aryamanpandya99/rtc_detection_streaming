"""
TODO: Update here once changed things around
"""

import argparse
import asyncio

from aiortc import RTCPeerConnection
from aiortc.contrib.signaling import add_signaling_arguments, create_signaling

from rtc_signal_handlers import consume_signaling
from video_track import WebCamTrack


async def run_server(pc, signaling):
    """
    Main function that initializes the server and handles the signaling process.

    Args:
        pc (RTCPeerConnection): The RTCPeerConnection object.
        signaling (Signaling): The signaling object.

    Returns:
        None
    """
    await signaling.connect()

    pc.addTrack(WebCamTrack())

    # Create an offer
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    print("Created offer")

    # Send the offer to the signaling server
    await signaling.send(pc.localDescription)
    print("Sent offer to signaling server")

    await consume_signaling(pc, signaling)


def main():
    """
    Entry point of the program.

    Args:
        None

    Returns:
        None
    """
    parser = argparse.ArgumentParser(description="Server for the face detection system")
    add_signaling_arguments(parser)
    args = parser.parse_args()

    signaling = create_signaling(args)
    pc = RTCPeerConnection()

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_server(pc, signaling))
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(pc.close())
        loop.run_until_complete(signaling.close())


if __name__ == "__main__":
    main()
