"""
Unit tests for server.py
Author: Aryaman Pandya
Assignment for Nimble Robotics 
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from rtc_signal_handlers import consume_signaling, handle_signaling
from aiortc import RTCSessionDescription, RTCIceCandidate
from aiortc.contrib.signaling import BYE


@pytest.mark.asyncio
async def test_handle_signaling_offer():
    pc = AsyncMock()
    signaling = AsyncMock()

    obj = MagicMock(spec=RTCSessionDescription)
    obj.type = "offer"
    signaling.receive.return_value = obj

    await handle_signaling(signaling, pc)

    signaling.receive.assert_called_once()
    pc.setRemoteDescription.assert_called_once_with(obj)
    pc.setLocalDescription.assert_called_once()
    signaling.send.assert_called_once_with(pc.localDescription)


@pytest.mark.asyncio
async def test_handle_signaling_answer():
    pc = AsyncMock()
    signaling = AsyncMock()

    obj = MagicMock(spec=RTCSessionDescription)
    obj.type = "answer"
    signaling.receive.return_value = obj

    await handle_signaling(signaling, pc)

    signaling.receive.assert_called_once()
    pc.setRemoteDescription.assert_called_once_with(obj)
    pc.setLocalDescription.assert_not_called()
    signaling.send.assert_not_called()


@pytest.mark.asyncio
async def test_handle_signaling_ice_candidate():
    pc = AsyncMock()
    signaling = AsyncMock()

    obj = MagicMock(spec=RTCIceCandidate)
    signaling.receive.return_value = obj

    await handle_signaling(signaling, pc)

    signaling.receive.assert_called_once()
    pc.addIceCandidate.assert_called_once_with(obj)


@pytest.mark.asyncio
async def test_handle_signaling_bye():
    pc = AsyncMock()
    signaling = AsyncMock()

    signaling.receive.return_value = BYE

    result = await handle_signaling(signaling, pc)

    signaling.receive.assert_called_once()
    assert result == -1

if __name__ == "__main__":
    pytest.main()
