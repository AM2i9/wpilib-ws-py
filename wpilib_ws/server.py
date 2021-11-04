import logging
import asyncio
import json
from typing import Union

from websockets import serve
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

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
        self._background_tasks = []
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

    async def _ws_handler(self, ws, path):
        """
        Base handler for websocket connections. Only one connection is allowed
        at a time to prevent duplicate connections.
        """

        if self._connected:
            await ws.send("HTTP/1.1 409 Conflict\r\n")
            await ws.lose()

        try:
            if path == "/wpilibws" and not self._connected:
                self._log.info(f"Client connected: {ws.remote_address}")

                self._connected = True
                self._ws = ws
                self._start_background_tasks()

                async for msg in ws:
                    data = json.loads(msg)
                    
                    if not self.verify_data(data):
                        self._log.debug(f"Ignoring invalid data: {data}")
                    else:
                        self._log.debug(f"Recieved message data: {data}")
                        event = MessageEvent.from_dict(data)
                        await self._handle_message(event)
        except ConnectionClosedError as e:
            self._log.info(f"Socket Closed ({e.code}): {e.reason}")
        finally:
            self._connected = False
            self._log.info("Socket Disconnected")

    
    async def send_payload(self, payload):
        """
        Send a JSON payload over the websocket
        """
        await self._send_ws_message(json.dumps(payload))

    async def _send_ws_message(self, message):
        try:
            await self._ws.send(message)
        except ConnectionClosedError:
            self._log.debug("Could not send message because the socket was closed")

    def _start_background_tasks(self):
        self._loop.create_task(self._run_while_connected())
    
    async def _run_while_connected(self):
        if not self._background_tasks:
            self._log.debug("No background tasks, canceling")
            return

        try:
            while True:
                if not self._ws.closed:
                    await asyncio.gather(*(task() for task in self._background_tasks))
                else:
                    break
        except ConnectionClosedOK:
            pass
    
    def while_connected(self, buffer=0.05):
        """
        While robot code is connected, run the given coroutine in the
        background. This is best for sending payloads to the server for devices
        such as encoders, gyros, etc.
        """
        def wrapper(coro):
            async def wrapped():
                await coro()
                await asyncio.sleep(buffer)
            self._background_tasks.append(wrapped)
            return coro
        return wrapper

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
    
    async def async_run(self, address="0.0.0.0", port=3300):
        """
        Start the WebSocket server
        """
        self._loop = asyncio.get_event_loop()
        async with serve(self._ws_handler, address, port) as s:
            print(f"Listening on ws://{address}:{port}")
            await asyncio.Future()

    def run(self, address="0.0.0.0", port=3300):
        """
        Start the WebSocket server. Non-async alias for `async_run`.
        """
        asyncio.run(self.async_run(address, port))
