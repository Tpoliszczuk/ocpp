import asyncio
import websockets
from datetime import datetime
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call, call_result
from ocpp.routing import on

class ChargePoint(cp):
    @on("RemoteStartTransaction")
    async def on_remote_start_transaction(self, id_tag, **kwargs):
        print(f"Otrzymano polecenie rozpoczęcia ładowania dla: {id_tag}")
        # Symulacja rozpoczęcia ładowania
        return call_result.RemoteStartTransaction(status="Accepted")
    
    @on("RemoteStopTransaction") 
    async def on_remote_stop_transaction(self, transaction_id, **kwargs):
        print(f"Otrzymano polecenie zatrzymania transakcji: {transaction_id}")
        # Symulacja zatrzymania ładowania
        return call_result.RemoteStopTransaction(status="Accepted")
    
    @on("ChangeConfiguration")
    async def on_change_configuration(self, key, value, **kwargs):
        print(f"Otrzymano polecenie zmiany konfiguracji: {key} = {value}")
        # Symulacja akceptacji zmiany konfiguracji
        if key == "Url":
            print(f"Zmieniam URL serwera na: {value}")
            return call_result.ChangeConfiguration(status="Accepted")
        else:
            return call_result.ChangeConfiguration(status="NotSupported")
    async def run(self):
        # Pierwsze logowanie stacji
        request = call.BootNotification(
            charge_point_model="MyModel",
            charge_point_vendor="MyVendor"
        )
        response = await self.call(request)
        print("BootNotification response:", response)

        # Wysyłanie statusu co pewien czas
        if self.id == "CP_1":
            status_request = call.StatusNotification(
                connector_id=1,
                error_code="NoError",
                status="Available",
                timestamp=datetime.utcnow().isoformat()
            )
            resp = await self.call(status_request)
            print("StatusNotification sent:", resp)
            await asyncio.sleep(10)  # co 10 sekund
        else:
            # Dla CP_2 wysyłamy Heartbeat
            heartbeat_request = call.Heartbeat()
            resp = await self.call(heartbeat_request)
            print("Heartbeat sent:", resp)
            await asyncio.sleep(15)  # co 15 sekund

async def main():
    # Azure deployment - WebSocket na tym samym porcie co HTTP
    #azure_url = "wss://ocpp-cwehcmh6gyg9gycr.northeurope-01.azurewebsites.net"
    
    azure_url = "wss://20.107.224.54"  # Dla testów lokalnych
    
    async with websockets.connect(f"{azure_url}/CP_1") as ws1:
        cp1 = ChargePoint("CP_1", ws1)
    
            
        await asyncio.gather(
                cp1.start(), cp1.run()
            )

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            print(f"Error: {e}")
            import time
            time.sleep(5)
