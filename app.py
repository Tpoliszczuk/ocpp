import asyncio
import threading
from flask import Flask
import websockets
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result, call
from datetime import datetime
import os

app = Flask(__name__)

class CentralSystem(cp):
    async def send_remote_start(self, id_tag="RFID123"):
        """Wysyła polecenie rozpoczęcia ładowania do klienta"""
        request = call.RemoteStartTransaction(id_tag=id_tag)
        response = await self.call(request)
        print(f"RemoteStartTransaction response: {response}")
        return response
    
    async def send_change_configuration(self, key, value):
        """Wysyła polecenie zmiany konfiguracji do klienta"""
        request = call.ChangeConfiguration(key=key, value=value)
        response = await self.call(request)
        print(f"ChangeConfiguration response: {response}")
        return response
    
    @on("BootNotification")
    async def on_boot_notification(self, charge_point_vendor, charge_point_model, **kwargs):
        print(f"BootNotification received from {self.id}")
        print(f"Vendor: {charge_point_vendor}, Model: {charge_point_model}")
        
        # Po BootNotification, wyślij zmianę konfiguracji URL
        asyncio.create_task(self.send_url_configuration())
        
        return call_result.BootNotification(
            current_time=datetime.utcnow().isoformat() + "Z",
            interval=30,
            status="Accepted"
        )
    
    async def send_url_configuration(self):
        """Wysyła konfigurację URL po krótkim opóźnieniu"""
        await asyncio.sleep(2)  # Czekaj 2 sekundy po BootNotification
        await self.send_change_configuration("Url", "ws://47.101.173.122:8887")
    
    @on("StatusNotification")
    async def on_status_notification(self, connector_id, error_code, status, **kwargs):
        print(f"StatusNotification received from {self.id}")
        print(f"Connector {connector_id}: {status} (Error: {error_code})")
        return call_result.StatusNotification()
    
    @on("Heartbeat")
    async def on_heartbeat(self, **kwargs):
        print(f"Heartbeat received from {self.id}")
        return call_result.Heartbeat(
            current_time=datetime.utcnow().isoformat() + "Z"
        )

async def on_connect(websocket):
    try:
        # For websockets 15.x, we need to use the request object
        path = websocket.request.path if hasattr(websocket, 'request') else websocket.path
        charge_point_id = path.strip("/")
        print(f"New connection from charge point: {charge_point_id}")
        cp = CentralSystem(charge_point_id, websocket)
        await cp.start()
    except Exception as e:
        print(f"Error handling connection: {e}")
        import traceback
        traceback.print_exc()
        await websocket.close()

async def start_websocket_server():
    """Uruchamia serwer WebSocket w tle"""
    port = int(os.environ.get('PORT', 8000))
    server = await websockets.serve(
        on_connect, 
        "0.0.0.0", 
        port,
        process_request=None
    )
    print(f"OCPP WebSocket server listening on ws://0.0.0.0:{port}")
    await server.wait_closed()

def run_websocket_server():
    """Uruchamia serwer WebSocket w osobnym wątku"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_websocket_server())

@app.route('/')
def index():
    return {
        "status": "OCPP Central System Running",
        "websocket_endpoint": f"ws://{os.environ.get('WEBSITE_HOSTNAME', 'localhost')}",
        "protocol": "OCPP 1.6j"
    }

@app.route('/health')
def health():
    return {"status": "healthy"}

# Uruchom serwer WebSocket w tle przy starcie aplikacji
websocket_thread = threading.Thread(target=run_websocket_server, daemon=True)
websocket_thread.start()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
