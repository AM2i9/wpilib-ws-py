import asyncio
from aiohttp import web

class WPILibWsServer:
    def __init__(self, address="0.0.0.0", port=3300, uri="/wpilibws", loop=None):
        self._address = address
        self._port = port
        self._uri = uri
        self._connected = False
        self._loop = loop
    
    async def _ws_handler(self, request):

        if self._connected:
            print("Already connected")
            return
        else:
            print("Connected")
            self._connected = True
        
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        try:
            while True:
                data = await ws.receive_json(2)
                print(data)
        except asyncio.TimeoutError:
            print("Connection timed out")
        
        self._connected = False
        print("Connection Closed")
    
    async def build_app(self):
        app = web.Application()
        app.add_routes([web.get(self._uri, self._ws_handler)])
            
        return app
