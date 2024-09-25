"""
Unit tests for server.py
Author: Aryaman Pandya
"""
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiortc import RTCIceCandidate, RTCSessionDescription
from aiortc.contrib.signaling import BYE

from ..rtc_signal_handlers import handle_signaling


@pytest.mark.asyncio
async def test_handle_signaling_offer():
    """
    Test the handle_signaling function with an offer message.
    """
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
    """
    Test the handle_signaling function with an answer message.
    """
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
    """
    Test the handle_signaling function with an ICE candidate message.
    """
    pc = AsyncMock()
    signaling = AsyncMock()

    obj = MagicMock(spec=RTCIceCandidate)
    signaling.receive.return_value = obj

    await handle_signaling(signaling, pc)

    signaling.receive.assert_called_once()
    pc.addIceCandidate.assert_called_once_with(obj)


@pytest.mark.asyncio
async def test_handle_signaling_bye():
    """
    Test the handle_signaling function with a BYE message.
    """
    pc = AsyncMock()
    signaling = AsyncMock()

    signaling.receive.return_value = BYE

    result = await handle_signaling(signaling, pc)

    signaling.receive.assert_called_once()
    assert result == -1


if __name__ == "__main__":
    pytest.main()
