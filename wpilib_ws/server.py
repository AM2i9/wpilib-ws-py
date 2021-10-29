import logging
import asyncio

from aiohttp import web

from wpilib_ws import utils


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

        try:
            while True:
                data = await ws.receive_json(timeout=2)
                self._log.debug(f">Incoming WS MSG: {data}")
        except asyncio.TimeoutError:
            self._log.info("Timed out")

        self._connected = False
        self._log.info(f"Socket Closed ({ws.close_code}): {ws.reason}")

    async def build_app(self):
        app = web.Application(logger=self._log)
        app.add_routes([web.get(self._uri, self._ws_handler)])

        return app
