import asyncio
import websockets
import logging
from datetime import datetime
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result, call
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CentralSystem(cp):
    async def send_remote_start(self, id_tag="RFID123"):
        """Wysyła polecenie rozpoczęcia ładowania do klienta"""
        request = call.RemoteStartTransaction(id_tag=id_tag)
        response = await self.call(request)
        logger.info(f"RemoteStartTransaction response: {response}")
        return response
    
    async def send_change_configuration(self, key, value):
        """Wysyła polecenie zmiany konfiguracji do klienta"""
        request = call.ChangeConfiguration(key=key, value=value)
        response = await self.call(request)
        logger.info(f"ChangeConfiguration response: {response}")
        return response
    @on("BootNotification")
    async def on_boot_notification(self, charge_point_vendor, charge_point_model, **kwargs):
        logger.info(f"BootNotification received from {self.id}")
        logger.info(f"Vendor: {charge_point_vendor}, Model: {charge_point_model}")
        
        # Po BootNotification, wyślij zmianę konfiguracji URL
        asyncio.create_task(self.send_url_configuration())
        
        return call_result.BootNotification(
            current_time=datetime.now().isoformat() + "Z",
            interval=30,
            status="Accepted"
        )
    
    async def send_url_configuration(self):
        """Wysyła konfigurację URL po krótkim opóźnieniu"""
        await asyncio.sleep(2)  # Czekaj 2 sekundy po BootNotification
        await self.send_change_configuration("Url", "ws://47.101.173.122:8887")
    
    @on("StatusNotification")
    async def on_status_notification(self, connector_id, error_code, status, **kwargs):
        logger.info(f"StatusNotification received from {self.id}")
        logger.info(f"Connector {connector_id}: {status} (Error: {error_code})")
        return call_result.StatusNotification()
    
    @on("Heartbeat")
    async def on_heartbeat(self, **kwargs):
        logger.info(f"Heartbeat received from {self.id}")
        return call_result.Heartbeat(
            current_time=datetime.now().isoformat() + "Z"
        )

async def on_connect(websocket):
    try:
        # For websockets 15.x, we need to use the request object
        path = websocket.request.path if hasattr(websocket, 'request') else websocket.path
        charge_point_id = path.strip("/")
        logger.info(f"New connection from charge point: {charge_point_id}")
        cp = CentralSystem(charge_point_id, websocket)
        await cp.start()
    except Exception as e:
        logger.error(f"Error handling connection: {e}")
        import traceback
        logger.error(traceback.format_exc())
        await websocket.close()

async def main():
    # For Azure deployment, bind to 0.0.0.0 and use PORT env var
    port = int(os.environ.get('PORT', 8000))
    server = await websockets.serve(
        on_connect, 
        "0.0.0.0", 
        port,
        process_request=None
    )
    logger.info(f"Central system listening on ws://0.0.0.0:{port}")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())


