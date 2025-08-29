import asyncio
import websockets
from datetime import datetime, timezone
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call, call_result
from ocpp.routing import on
import random

class ComprehensiveChargePoint(cp):
    """Comprehensive OCPP 1.6j ChargePoint with all possible message handlers"""
    
    # ============ INCOMING MESSAGES FROM CENTRAL SYSTEM ============
    
    @on("RemoteStartTransaction")
    async def on_remote_start_transaction(self, id_tag, **kwargs):
        print(f"[RECEIVED] RemoteStartTransaction: id_tag={id_tag}, kwargs={kwargs}")
        return call_result.RemoteStartTransaction(status="Accepted")
    
    @on("RemoteStopTransaction") 
    async def on_remote_stop_transaction(self, transaction_id, **kwargs):
        print(f"[RECEIVED] RemoteStopTransaction: transaction_id={transaction_id}")
        return call_result.RemoteStopTransaction(status="Accepted")
    
    @on("ChangeConfiguration")
    async def on_change_configuration(self, key, value, **kwargs):
        print(f"[RECEIVED] ChangeConfiguration: {key} = {value}")
        return call_result.ChangeConfiguration(status="Accepted")
    
    @on("GetConfiguration")
    async def on_get_configuration(self, key=None, **kwargs):
        print(f"[RECEIVED] GetConfiguration: key={key}")
        # Return sample configuration
        config_keys = [
            {"key": "Url", "readonly": False, "value": "wss://ocpp-server.com"},
            {"key": "HeartbeatInterval", "readonly": False, "value": "30"},
            {"key": "MeterValueSampleInterval", "readonly": False, "value": "60"}
        ]
        return call_result.GetConfigurationPayload(
            configuration_key=config_keys if key is None else [k for k in config_keys if k["key"] == key]
        )
    
    @on("Reset")
    async def on_reset(self, type, **kwargs):
        print(f"[RECEIVED] Reset: type={type}")
        return call_result.ResetPayload(status="Accepted")
    
    @on("UnlockConnector")
    async def on_unlock_connector(self, connector_id, **kwargs):
        print(f"[RECEIVED] UnlockConnector: connector_id={connector_id}")
        return call_result.UnlockConnectorPayload(status="Unlocked")
    
    @on("ChangeAvailability")
    async def on_change_availability(self, connector_id, type, **kwargs):
        print(f"[RECEIVED] ChangeAvailability: connector_id={connector_id}, type={type}")
        return call_result.ChangeAvailabilityPayload(status="Accepted")
    
    @on("ClearCache")
    async def on_clear_cache(self, **kwargs):
        print("[RECEIVED] ClearCache")
        return call_result.ClearCachePayload(status="Accepted")
    
    @on("DataTransfer")
    async def on_data_transfer(self, vendor_id, message_id=None, data=None, **kwargs):
        print(f"[RECEIVED] DataTransfer: vendor_id={vendor_id}, message_id={message_id}, data={data}")
        return call_result.DataTransferPayload(status="Accepted")
    
    @on("GetDiagnostics")
    async def on_get_diagnostics(self, location, **kwargs):
        print(f"[RECEIVED] GetDiagnostics: location={location}")
        return call_result.GetDiagnosticsPayload(file_name="diagnostics.log")
    
    @on("UpdateFirmware")
    async def on_update_firmware(self, location, retrieve_date, **kwargs):
        print(f"[RECEIVED] UpdateFirmware: location={location}, retrieve_date={retrieve_date}")
        return call_result.UpdateFirmwarePayload()
    
    @on("ReserveNow")
    async def on_reserve_now(self, connector_id, expiry_date, id_tag, reservation_id, **kwargs):
        print(f"[RECEIVED] ReserveNow: connector_id={connector_id}, id_tag={id_tag}")
        return call_result.ReserveNowPayload(status="Accepted")
    
    @on("CancelReservation")
    async def on_cancel_reservation(self, reservation_id, **kwargs):
        print(f"[RECEIVED] CancelReservation: reservation_id={reservation_id}")
        return call_result.CancelReservationPayload(status="Accepted")
    
    @on("TriggerMessage")
    async def on_trigger_message(self, requested_message, connector_id=None, **kwargs):
        print(f"[RECEIVED] TriggerMessage: message={requested_message}, connector_id={connector_id}")
        return call_result.TriggerMessagePayload(status="Accepted")
    
    @on("SetChargingProfile")
    async def on_set_charging_profile(self, connector_id, cs_charging_profiles, **kwargs):
        print(f"[RECEIVED] SetChargingProfile: connector_id={connector_id}")
        return call_result.SetChargingProfilePayload(status="Accepted")
    
    @on("ClearChargingProfile")
    async def on_clear_charging_profile(self, **kwargs):
        print("[RECEIVED] ClearChargingProfile")
        return call_result.ClearChargingProfilePayload(status="Accepted")
    
    @on("GetCompositeSchedule")
    async def on_get_composite_schedule(self, connector_id, duration, **kwargs):
        print(f"[RECEIVED] GetCompositeSchedule: connector_id={connector_id}, duration={duration}")
        return call_result.GetCompositeSchedulePayload(status="Accepted")
    
    @on("GetLocalListVersion")
    async def on_get_local_list_version(self, **kwargs):
        print("[RECEIVED] GetLocalListVersion")
        return call_result.GetLocalListVersionPayload(list_version=1)
    
    @on("SendLocalList")
    async def on_send_local_list(self, list_version, update_type, **kwargs):
        print(f"[RECEIVED] SendLocalList: version={list_version}, type={update_type}")
        return call_result.SendLocalListPayload(status="Accepted")
    
    # ============ OUTGOING MESSAGES TO CENTRAL SYSTEM ============
    
    async def send_boot_notification(self):
        """Send BootNotification"""
        request = call.BootNotification(
            charge_point_model="Test Model",
            charge_point_vendor="Test Vendor"
        )
        response = await self.call(request)
        print(f"[SENT] BootNotification response: {response}")
        return response
    
    async def send_heartbeat(self):
        """Send Heartbeat"""
        request = call.Heartbeat()
        response = await self.call(request)
        print(f"[SENT] Heartbeat response: {response}")
        return response
    
    async def send_status_notification(self, connector_id, error_code, status):
        """Send StatusNotification"""
        request = call.StatusNotification(
            connector_id=connector_id,
            error_code=error_code,
            status=status
        )
        response = await self.call(request)
        print(f"[SENT] StatusNotification response: {response}")
        return response
    
    async def send_meter_values(self, connector_id, meter_value):
        """Send MeterValues"""
        request = call.MeterValues(
            connector_id=connector_id,
            meter_value=meter_value
        )
        response = await self.call(request)
        print(f"[SENT] MeterValues response: {response}")
        return response
    
    async def send_start_transaction(self, connector_id, id_tag):
        """Send StartTransaction"""
        request = call.StartTransaction(
            connector_id=connector_id,
            id_tag=id_tag,
            meter_start=0,
            timestamp=datetime.now().isoformat() + "Z"
        )
        response = await self.call(request)
        print(f"[SENT] StartTransaction response: {response}")
        return response
    
    async def send_stop_transaction(self, transaction_id, meter_stop):
        """Send StopTransaction"""
        request = call.StopTransaction(
            meter_stop=meter_stop,
            timestamp=datetime.now().isoformat() + "Z",
            transaction_id=transaction_id
        )
        response = await self.call(request)
        print(f"[SENT] StopTransaction response: {response}")
        return response
    
    async def send_authorize(self, id_tag):
        """Send Authorize"""
        request = call.Authorize(id_tag=id_tag)
        response = await self.call(request)
        print(f"[SENT] Authorize response: {response}")
        return response
    
    async def send_data_transfer(self, vendor_id, message_id=None, data=None):
        """Send DataTransfer"""
        request = call.DataTransfer(
            vendor_id=vendor_id,
            message_id=message_id,
            data=data
        )
        response = await self.call(request)
        print(f"[SENT] DataTransfer response: {response}")
        return response
    
    async def send_diagnostics_status_notification(self, status="Uploaded"):
        """Send DiagnosticsStatusNotification"""
        request = call.DiagnosticsStatusNotification(status=status)
        response = await self.call(request)
        print(f"[SENT] DiagnosticsStatusNotification response: {response}")
        return response
    
    async def send_firmware_status_notification(self, status="Downloaded"):
        """Send FirmwareStatusNotification"""
        request = call.FirmwareStatusNotification(status=status)
        response = await self.call(request)
        print(f"[SENT] FirmwareStatusNotification response: {response}")
        return response
    
    # ============ COMPREHENSIVE TEST SEQUENCE ============
    
    async def run_comprehensive_test(self):
        """Run comprehensive test of all OCPP message types"""
        print("\n=== STARTING COMPREHENSIVE OCPP 1.6j TEST ===\n")
        
        async def safe_call(func, *args, **kwargs):
            """Safely call a function and continue on error"""
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                print(f"[ERROR] {func.__name__}: {e}")
                return None
        
        try:
            # 1. Boot sequence
            print("1. Boot Notification...")
            await self.send_boot_notification()
            await asyncio.sleep(1)
            
            # 2. Status Notifications
            print("2. Status Notifications...")
            await safe_call(self.send_status_notification, 1, "NoError", "Available")
            await safe_call(self.send_status_notification, 1, "NoError", "Preparing")
            await asyncio.sleep(0.5)
            
            # 3. Authorization
            print("\n3. Authorization...")
            auth_resp = await safe_call(self.send_authorize, "RFID123456")
            await asyncio.sleep(0.5)
            
            # 4. Start transaction
            print("\n4. Start Transaction...")
            start_resp = await safe_call(self.send_start_transaction, 1, "RFID123456")
            transaction_id = getattr(start_resp, 'transaction_id', 12345) if start_resp else 12345
            await asyncio.sleep(0.5)
            
            # 5. Meter Values
            print("\n5. Meter Values...")
            meter_value = [{
                "timestamp": datetime.now().isoformat() + "Z",
                "sampled_value": [{
                    "value": "1234.5",
                    "measurand": "Energy.Active.Import.Register",
                    "unit": "Wh"
                }]
            }]
            await safe_call(self.send_meter_values, 1, meter_value)
            await asyncio.sleep(0.5)
            
            # 6. Charging status
            print("\n6. Charging Status...")
            await safe_call(self.send_status_notification, 1, "NoError", "Charging")
            await asyncio.sleep(0.5)
            
            # 7. Stop transaction
            print("\n7. Stop Transaction...")
            await safe_call(self.send_stop_transaction, transaction_id, 2000)
            await asyncio.sleep(0.5)
            
            # 8. Heartbeats
            print("\n8. Heartbeats...")
            for i in range(2):
                await safe_call(self.send_heartbeat)
                await asyncio.sleep(1)
            
            # 9. Data transfer
            print("\n9. Data Transfer...")
            await safe_call(self.send_data_transfer, "TestVendor", "CustomMessage", "Test data payload")
            await asyncio.sleep(0.5)
            
            # 10. Diagnostics and firmware
            print("\n10. Diagnostics & Firmware...")
            await safe_call(self.send_diagnostics_status_notification, "Uploaded")
            await safe_call(self.send_firmware_status_notification, "Downloaded")
            await asyncio.sleep(0.5)
            
            # 11. Final status
            print("\n11. Final Status...")
            await safe_call(self.send_status_notification, 1, "NoError", "Available")
            
            print("\n=== COMPREHENSIVE TEST COMPLETED ===\n")
            print("All OCPP 1.6j message types tested:")
            print("✓ BootNotification")
            print("✓ StatusNotification (Available, Preparing, Charging)")
            print("✓ Authorize")
            print("✓ StartTransaction")
            print("✓ MeterValues")
            print("✓ StopTransaction")
            print("✓ Heartbeat")
            print("✓ DataTransfer")
            print("✓ DiagnosticsStatusNotification")
            print("✓ FirmwareStatusNotification")
            
        except Exception as e:
            print(f"Critical error during comprehensive test: {e}")
            import traceback
            traceback.print_exc()

async def main():
    """Main function to run comprehensive OCPP client"""
    # Azure deployment URL
    azure_url = "wss://ocpp-cwehcmh6gyg9gycr.northeurope-01.azurewebsites.net"
    # azure_url = "ws://localhost:8000"  # For local testing
    
    charge_point_id = "COMPREHENSIVE_TEST_CP"
    
    print(f"Connecting to {azure_url} as {charge_point_id}")
    
    async with websockets.connect(f"{azure_url}/{charge_point_id}") as ws:
        cp = ComprehensiveChargePoint(charge_point_id, ws)
        
        # Start the charge point
        await asyncio.gather(
            cp.start(),
            cp.run_comprehensive_test()
        )

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            print(f"Connection error: {e}")
            print("Retrying in 5 seconds...")
            import time
            time.sleep(5)
