import logging
import asyncio
from typing import Union

from aiohttp import web

from wpilib_ws import utils
from wpilib_ws.hardware import DeviceType, CANDeviceType


class InvalidDeviceError(Exception):
    def __init__(self, device: str):
        self.device = device
        self.message = f"Device type '{device}' does not exists or cannot be handled."
        super().__init__(self.message)


class MessageEvent:

    type: str
    device: str
    data: dict

    def __init__(self, type: Union[DeviceType, CANDeviceType], device: str, data: dict):
        self.type = type
        self.device = device
        self.payload = data

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
    """
    An implementation of the WPILib WebSocket server. Specifications on payload
    data and other information about the API can be found
    [here](https://github.com/wpilibsuite/allwpilib/blob/main/simulation/halsim_ws_core/doc/hardware_ws_api.md).
    """

    def __init__(
        self,
        uri="/wpilibws",
        loop=None,
        logger=None,
        debug=False,
    ):
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

        self._handlers = {}
        self._ws = None

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
                    (
                        DeviceType.device_exists(data.get("type"))
                        or CANDeviceType.device_exists(data.get("type"))
                    ),
                )
            )

    async def _ws_handler(self, request):
        """
        Base handler for websocket connections. Only one connection is allowed
        at a time to prevent duplicate connections.
        """

        ws = web.WebSocketResponse()
        await ws.prepare(request)

        if self._connected:
            await ws.write(b"HTTP/1.1 409 Conflict\r\n")
            self._log.info("Socket already active")
            return
        else:
            self._ws = ws
            self._log.info("Client connected")
            self._connected = True

        while True:
            try:
                data = await self._ws.receive_json(timeout=2)

                if not self.verify_data(data):
                    self._log.debug(f"Ignoring Invalid Data: {data}")
                else:
                    self._log.debug(f">Incoming WS MSG: {data}")
                    event = MessageEvent.from_dict(data)
                    await self._handle_message(event)
            except asyncio.TimeoutError:
                self._log.info("Timed out")
                break
            except InvalidDeviceError as e:
                self._log.error(e)

        self._connected = False
        self._log.info(f"Socket Closed ({self._ws.close_code}): {self._ws.reason}")
        self._ws = None

    def on_message(self, device_type: Union[str, DeviceType, CANDeviceType] = None):
        """
        Decorator for creating a message handler for all or a specific device
        type coming overthe websocket.
        """
        if isinstance(device_type, (DeviceType, CANDeviceType)):
            device_type = device_type.value

        def wrapper(func):
            event_name = device_type or "message"
            self.add_handler(event_name, func)
            return func

        return wrapper

    def add_handler(self, event, func):
        """
        Add a handler for a websocket message event.
        """
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(func)

    async def _handle_message(self, event: MessageEvent):
        """
        Handle incoming messages, and call the appropriate handlers.
        """

        for item in self._handlers.items():
            if item[0] in (event.type.value, "message"):
                for func in item[1]:
                    await func(event)

    def build_app(self) -> web.Application:
        """
        Build a `aiohttp.web.Application`. This can be used to run the server
        with webserver softwares such as Gunicorn or Uvicorn.
        `WPILibWsServer.run()` can be used during development to use the
        aiohttp debug server.
        """
        app = web.Application(logger=self._log)
        app.add_routes([web.get(self._uri, self._ws_handler)])

        return app

    def run(self, address="0.0.0.0", port=3300):
        """
        Run the server using the aiohttp debug server.
        **This is not suggested for production use.** Web servers such as
        Gunicorn or Uvicorn are suggested for running aiohttp applications in
        production.
        """
        app = self.build_app()
        web.run_app(app, host=address, port=port)
