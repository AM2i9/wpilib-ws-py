import logging
import asyncio
from dataclasses import dataclass

from aiohttp import web

from wpilib_ws import utils
from wpilib_ws.hardware import DeviceType, CANDeviceType


class InvalidDeviceError(Exception):
    def __init__(self, device: str):
        self.device = device
        self.message = f"Device type '{device}' does not exists or cannot be handled."
        super().__init__(self.message)


@dataclass
class MessageEvent:

    type: str
    device: str
    data: dict

    @classmethod
    def from_dict(cls, message: dict):
        device_type = message["type"]
        try:
            if device_type.startswith("CAN"):
                _type = CANDeviceType(device_type)
            else:
                _type = DeviceType(device_type)

            return cls(_type, message["device"], message["data"])
        except ValueError:
            raise InvalidDeviceError(device_type)


class WPILibWsServer:
    def __init__(
        self,
        address="0.0.0.0",
        port=3300,
        uri="/wpilibws",
        loop=None,
        logger=None,
        debug=False,
    ):
        self._address = address
        self._port = port
        self._uri = uri
        self._connected = False
        self._loop = loop

        if logger is None:
            self._log = utils.setup_default_logger()
        else:
            self._log = logger

        self._debug = debug
        if self._debug:
            self._log.setLevel(logging.DEBUG)

    def verify_data(self, data: dict):
        """
        Verify that the recieved message is valid.

        As per the WPILib protocol, the server will ignore messages that:
        - Are not a dict
        - Have no 'type' key, 'device' key, or 'data' key
        - Have a 'type' or 'device' key that is not a string
        - Have a 'data' value that is not a dict
        - Have a 'type' value that the client or server does not recognize
        """
        if not isinstance(data, dict):
            return False
        else:
            return all(
                (
                    isinstance(data.get("type"), str),
                    isinstance(data.get("device"), str),
                    isinstance(data.get("data"), dict),
                )
            )

    async def _ws_handler(self, request):

        ws = web.WebSocketResponse()
        await ws.prepare(request)

        if self._connected:
            await ws.write(b"HTTP/1.1 409 Conflict\r\n")
            self._log.info("Socket already active")
            return
        else:
            self._log.info("Client connected")
            self._connected = True

        while True:
            try:
                data = await ws.receive_json(timeout=2)

                if not self.verify_data(data):
                    self._log.debug(f"Ignoring Invalid Data: {data}")
                else:
                    self._log.debug(f">Incoming WS MSG: {data}")
                    event = MessageEvent.from_dict(data)
                    await self.on_message(event)
            except asyncio.TimeoutError:
                self._log.info("Timed out")
                break
            except InvalidDeviceError as e:
                self._log.error(e)

        self._connected = False
        self._log.info(f"Socket Closed ({ws.close_code}): {ws.reason}")

    async def on_message(self, event):
        pass

    async def build_app(self):
        app = web.Application(logger=self._log)
        app.add_routes([web.get(self._uri, self._ws_handler)])

        return app
