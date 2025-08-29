from datetime import datetime, timezone
import asyncio
import websockets
import logging
import os
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call_result, call, datatypes, enums

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CentralSystem(cp):
    """Comprehensive OCPP 1.6j Central System with all message handlers"""
    
    def __init__(self, id, connection):
        super().__init__(id, connection)
        self.transactions = {}  # Track active transactions
        self.reservations = {}  # Track reservations
    
    # ============ OUTGOING MESSAGES TO CHARGE POINT ============
    
    async def send_remote_start(self, id_tag="RFID123", connector_id=1):
        """Send RemoteStartTransaction"""
        request = call.RemoteStartTransaction(
            id_tag=id_tag,
            connector_id=connector_id
        )
        response = await self.call(request)
        logger.info(f"RemoteStartTransaction response: {response}")
        return response
    
    async def send_remote_stop(self, transaction_id):
        """Send RemoteStopTransaction"""
        request = call.RemoteStopTransaction(transaction_id=transaction_id)
        response = await self.call(request)
        logger.info(f"RemoteStopTransaction response: {response}")
        return response
    
    async def send_change_configuration(self, key, value):
        """Send ChangeConfiguration"""
        request = call.ChangeConfiguration(key=key, value=value)
        response = await self.call(request)
        logger.info(f"ChangeConfiguration response: {response}")
        return response
    
    async def send_get_configuration(self, key=None):
        """Send GetConfiguration"""
        request = call.GetConfiguration(key=[key] if key else None)
        response = await self.call(request)
        logger.info(f"GetConfiguration response: {response}")
        return response
    
    async def send_reset(self, type="Soft"):
        """Send Reset"""
        request = call.Reset(type=type)
        response = await self.call(request)
        logger.info(f"Reset response: {response}")
        return response
    
    async def send_unlock_connector(self, connector_id):
        """Send UnlockConnector"""
        request = call.UnlockConnector(connector_id=connector_id)
        response = await self.call(request)
        logger.info(f"UnlockConnector response: {response}")
        return response
    
    async def send_change_availability(self, connector_id, type):
        """Send ChangeAvailability"""
        request = call.ChangeAvailability(connector_id=connector_id, type=type)
        response = await self.call(request)
        logger.info(f"ChangeAvailability response: {response}")
        return response
    
    # ============ INCOMING MESSAGES FROM CHARGE POINT ============
    
    @on("BootNotification")
    async def on_boot_notification(self, charge_point_vendor, charge_point_model, **kwargs):
        logger.info(f"BootNotification received from {self.id}")
        logger.info(f"Vendor: {charge_point_vendor}, Model: {charge_point_model}")
        logger.info(f"Additional info: {kwargs}")
        
        return call_result.BootNotification(
            current_time=datetime.now(timezone.utc).isoformat(),
            interval=30,
            status=enums.RegistrationStatus.accepted
        )
    
    @on("Heartbeat")
    async def on_heartbeat(self, **kwargs):
        logger.info(f"Heartbeat received from {self.id}")
        return call_result.Heartbeat(
            current_time=datetime.now(timezone.utc).isoformat()
        )
    
    @on("StatusNotification")
    async def on_status_notification(self, connector_id, error_code, status, **kwargs):
        logger.info(f"StatusNotification from {self.id}: Connector {connector_id} = {status} (Error: {error_code})")
        if kwargs:
            logger.info(f"Additional status info: {kwargs}")
        return call_result.StatusNotification()
    
    @on("MeterValues")
    async def on_meter_values(self, connector_id, meter_value, **kwargs):
        logger.info(f"MeterValues from {self.id}: Connector {connector_id}")
        for mv in meter_value:
            timestamp = mv.get('timestamp', 'N/A')
            logger.info(f"  Timestamp: {timestamp}")
            for sample in mv.get('sampled_value', []):
                measurand = sample.get('measurand', 'Unknown')
                value = sample.get('value', 'N/A')
                unit = sample.get('unit', '')
                logger.info(f"    {measurand}: {value} {unit}")
        return call_result.MeterValues()
    
    @on("StartTransaction")
    async def on_start_transaction(self, connector_id, id_tag, meter_start, timestamp, **kwargs):
        transaction_id = len(self.transactions) + 1
        self.transactions[transaction_id] = {
            'connector_id': connector_id,
            'id_tag': id_tag,
            'meter_start': meter_start,
            'timestamp': timestamp
        }
        logger.info(f"StartTransaction from {self.id}: Connector {connector_id}, ID: {id_tag}, Transaction: {transaction_id}")
        logger.info(f"  Meter start: {meter_start}, Time: {timestamp}")
        
        return call_result.StartTransaction(
            transaction_id=transaction_id,
            id_tag_info=datatypes.IdTagInfo(status=enums.AuthorizationStatus.accepted)
        )
    
    @on("StopTransaction")
    async def on_stop_transaction(self, meter_stop, timestamp, transaction_id, **kwargs):
        if transaction_id in self.transactions:
            transaction = self.transactions[transaction_id]
            energy_consumed = meter_stop - transaction['meter_start']
            logger.info(f"StopTransaction from {self.id}: Transaction {transaction_id}")
            logger.info(f"  Meter stop: {meter_stop}, Energy consumed: {energy_consumed}")
            logger.info(f"  Reason: {kwargs.get('reason', 'Unknown')}")
            del self.transactions[transaction_id]
        else:
            logger.warning(f"StopTransaction for unknown transaction {transaction_id}")
        
        return call_result.StopTransaction(
            id_tag_info=datatypes.IdTagInfo(status=enums.AuthorizationStatus.accepted)
        )
    
    @on("Authorize")
    async def on_authorize(self, id_tag, **kwargs):
        logger.info(f"Authorize from {self.id}: ID tag {id_tag}")
        # Simple authorization - accept all tags
        return call_result.Authorize(
            id_tag_info=datatypes.IdTagInfo(status=enums.AuthorizationStatus.accepted)
        )
    
    @on("DataTransfer")
    async def on_data_transfer(self, vendor_id, **kwargs):
        message_id = kwargs.get('message_id', 'N/A')
        data = kwargs.get('data', 'N/A')
        logger.info(f"DataTransfer from {self.id}: Vendor {vendor_id}, Message: {message_id}")
        logger.info(f"  Data: {data}")
        return call_result.DataTransfer(status=enums.DataTransferStatus.accepted)
    
    @on("DiagnosticsStatusNotification")
    async def on_diagnostics_status_notification(self, status, **kwargs):
        logger.info(f"DiagnosticsStatusNotification from {self.id}: {status}")
        return call_result.DiagnosticsStatusNotification()
    
    @on("FirmwareStatusNotification")
    async def on_firmware_status_notification(self, status, **kwargs):
        logger.info(f"FirmwareStatusNotification from {self.id}: {status}")
        return call_result.FirmwareStatusNotification()
    
    # ============ UTILITY METHODS ============
    
    async def get_active_transactions(self):
        """Get list of active transactions"""
        return self.transactions
    
    async def get_charge_point_status(self):
        """Get comprehensive charge point status"""
        return {
            'id': self.id,
            'active_transactions': len(self.transactions),
            'transactions': self.transactions,
            'reservations': self.reservations
        }

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


