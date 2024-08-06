
import multiprocessing.process
from DevOri.Aiomqtt_imp import make_deviceClient
from backend.aiomqtt_imp import MonadenKit, run_with_monaden_kit, make_bridge, make_bulb
import os
import asyncio
from DevOri.utils import any2bytes, LambdaSubscriber
from backend.Devices import IkeaColorLight
import multiprocessing
from aiomqtt import Message as Aiomessage

PREFIX = "zigbee2mqtt"
HOST = os.environ.get("MQTT_ADDR", "localhost")
PORT = 1883

async def main(kit: MonadenKit):
    print(await kit.lights[0].get_color())
    


async def main2():

    async with make_deviceClient(HOST,
                             PORT,
                             PREFIX,
                             verbose=False) as client:
        async with make_bridge(client) as bridge:   
            #a = await bridge.get_groups()
            #g_name = a[0]["friendly_name"]
            
            a = await bridge.get_devices()
            d_name = a[2]["friendly_name"]  
            print(d_name) 
            #await client.send(f"{g_name}/set",any2bytes({"state": "TOGGLE"}))
            await client.send(f"{d_name}/get",any2bytes({"state": ""}))
            lock = asyncio.locks.Lock()
            await lock.acquire()
            async def f(m: Aiomessage):
                print("callback", m.payload)
                lock.release()
            l = LambdaSubscriber[Aiomessage](f)
            await client.subscribe(l, "")
            await lock.acquire()
            
    
            
                
            

if __name__ == "__main__":
    #asyncio.run(run_with_monaden_kit(main,HOST,PORT,PREFIX,verbose=False))
    asyncio.run(main2())
   