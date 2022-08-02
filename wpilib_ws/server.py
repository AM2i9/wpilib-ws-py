from cgitb import handler
import logging
import asyncio
import json
from typing import Any, Coroutine, Mapping, Union

from websockets import serve
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from wpilib_ws import utils
from wpilib_ws.hardware import DeviceType, CANDeviceType


class Message:
    type: DeviceType | CANDeviceType
    device: str
    data: Mapping[str, Any]

    def __init__(self, type, device, data):
        self.type = type
        self.device = device
        self.data = data

    @classmethod
    def from_dict(cls, data: dict) -> "Message":

        if data["type"].startswith("CAN"):
            device_type = CANDeviceType(data["type"])
        else:
            device_type = DeviceType(data["type"])

        return cls(device_type, data["device"], data["data"])


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
        verbose=False,
        verbose_extreme=False,
    ):
        self._uri = uri
        self._connected = False
        self._loop = loop

        if logger is None:
            self._log = utils.setup_default_logger()
        else:
            self._log = logger

        self._verbose_extreme = verbose_extreme
        self._verbose = verbose or self._verbose_extreme
        if self._verbose:
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
            await ws.close(reason="Only one connection allowed at a time")
            self._log.debug(
                f"Client attempted to connect but was refused: {ws.remote_address[0]}:{ws.remote_address[1]}"
            )

        try:
            if path == self._uri and not self._connected:
                self._log.info(
                    f"Client connected: {ws.remote_address[0]}:{ws.remote_address[1]}"
                )

                self._connected = True
                self._ws = ws
                self._start_background_tasks()

                async for msg in ws:
                    data = json.loads(msg)

                    if not self.verify_data(data):
                        self._log.debug(f"Ignoring invalid data: {data}")
                    else:
                        if self._verbose_extreme:
                            self._log.debug(f"Recieved message data: {data}")
                        message = Message.from_dict(data)
                        await self._handle_message(message)

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
            if self._verbose_extreme:
                self._log.debug(f"Sent message: {message}")
        except ConnectionClosedError:
            self._log.debug(
                f"Could not send message because the socket was closed: {message}"
            )

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

        Example usage:
        ```py
        @server.while_connected()
        async def while_connected():
            await server.send_payload(
                {"type": "RoboRIO", "device": "", "data": {">vin_voltage": 12.0}}
            )
        ```
        """

        def wrapper(coro):
            self.add_coro_background_task(coro, buffer)
            return coro

        return wrapper

    def on_message(
        self,
        device_type: Union[str, DeviceType, CANDeviceType] = None,
        device_name: str = "",
    ):
        """
        Decorator for creating a message handler for all or a specific device
        type coming overthe websocket.

        Example usage:
        ```py
        @server.on_message("PWM")
        async def pwm_handler(message):
            ...
        ```
        ```py
        @server.on_message("SimDevice", "SPARK MAX")
        async def spark_max_handler(message):
            ...
        ```
        """
        if isinstance(device_type, (DeviceType, CANDeviceType)):
            device_type = device_type.value

        handler_name = device_type
        if device_name:
            handler_name += f":{device_name}"

        def wrapper(func):
            event_name = handler_name or "message"
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

    def add_coro_background_task(self, coro: Coroutine, buffer: float):
        """
        Add a Coroutine to the list of background tasks to run while connected.
        """

        async def wrapped():
            await coro()
            await asyncio.sleep(buffer)

        self._background_tasks.append(wrapped)

    async def _handle_message(self, event: Message):
        """
        Handle incoming messages, and call the appropriate handlers.
        """

        names = (event.type.value, "message")

        for item in self._handlers.items():
            if (
                ":" in item[0] and event.device.startswith(item[0].split(":")[1])
            ) or item[0] in names:
                for func in item[1]:
                    await func(event)

    async def async_run(self, address="0.0.0.0", port=3300):
        """
        Start the WebSocket server
        """
        self._loop = asyncio.get_event_loop()
        async with serve(self._ws_handler, address, port, ping_interval=None) as s:
            print(f"Listening on ws://{address}:{port}{self._uri}")
            await asyncio.Future()

    def run(self, address="0.0.0.0", port=3300):
        """
        Start the WebSocket server. Non-async alias for `async_run`.
        """
        asyncio.run(self.async_run(address, port))
