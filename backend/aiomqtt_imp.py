from typing import Dict, List, Callable, Coroutine, Sequence
from aiomqtt import Message as Message_aio
from .zigbee2mqttDevices import GetKinds, IkeaColorLight_devori, Communicator, IKEA_tradfri_remote_devori, RemoteKinds, Bridge, BridgeCategory
from DevOri.utils import bytes2any, any2bytes, MultiACM
from DevOri.Aiomqtt_imp import make_deviceClient
from .Devices import IkeaColorLight,IKEA_tradfri_remote
from dataclasses import dataclass

def m2d(message: Message_aio) -> Dict[str, str | int | float]:
    b: bytes = message.payload  # type: ignore
    if b == b"":
        return {}
    return bytes2any(b)

def sort_gets(message: Message_aio) -> GetKinds:
    keys = list(m2d(message).keys())
    if "state" in keys:
        return GetKinds.STATE
    
    return GetKinds.STATE

def make_bulb(friendly_name: str,
              communicator: Communicator[bytes, Message_aio],
              prefix:str = ""
              ) -> IkeaColorLight_devori[bytes, Message_aio]:
    bulb = IkeaColorLight_devori[bytes, Message_aio](friendly_name=friendly_name,
                                              communicator=communicator,
                                              prefix=prefix,
                                              sort_gets=sort_gets,
                                              dict2send_T=any2bytes,
                                              recive_T2dict=m2d
                                              ) 

    return bulb
def sort_remote_payload(message: Message_aio) -> RemoteKinds:
    b: bytes = message.payload  # type: ignore
    payload = bytes2any(b).keys() 
    
    if "action" in payload:
        return RemoteKinds.ACTION
    else:
        return RemoteKinds.BATTERYUPDATE
    

def make_remote(friendly_name: str,
              communicator: Communicator[bytes, Message_aio],
              prefix:str = "") -> IKEA_tradfri_remote_devori[bytes, Message_aio]:
    return IKEA_tradfri_remote_devori[bytes, Message_aio](friendly_name=friendly_name,
                communicator=communicator,
                category_sorter=sort_remote_payload,
                categories=RemoteKinds,
                dict2send_T=any2bytes,
                recive_T2dict=m2d,
                prefix=prefix)
def sort_bridge(message: Message_aio) -> BridgeCategory:
    return BridgeCategory.ALL
    
def make_bridge(
              communicator: Communicator[bytes, Message_aio],
              prefix:str = ""):
    return Bridge[bytes, Message_aio](
        communicator=communicator,
        category_sorter=sort_bridge,
        categories=BridgeCategory,
        dict2send_T=any2bytes,
        recive_T2dict=m2d,
        prefix=prefix)

@dataclass
class MonadenKit:
    TRADFRI_remotes: Sequence[IKEA_tradfri_remote]
    lights: Sequence[IkeaColorLight]
    all_lights: IkeaColorLight
    groups: Dict[str, IkeaColorLight]






async def run_with_monaden_kit(main: Callable[[MonadenKit], Coroutine[None, None, None]],
                               host: str, 
                               port: int, 
                               prefix: str, 
                               verbose: bool,

                               ):

    if verbose:
        print("Start monaden context")
    async with make_deviceClient(host, port, prefix, verbose) as client:
        async with make_bridge(client) as bridge:
            devices = await bridge.get_devices()
            lights: List[IkeaColorLight_devori[bytes, Message_aio]] = []
            remotes: List[IKEA_tradfri_remote_devori[bytes, Message_aio]] = []
            if len(devices) == 0:
                raise Exception("No devices found, is addapter/bridge connected?")

            
            for device in devices[1:]:
                
                modelId: str = device["model_id"]
                name: str = device["friendly_name"]
                if modelId == "TRADFRI bulb E14 CWS 470lm":
                    lights.append(make_bulb(name,client))
                elif modelId == "TRADFRI remote control":
                    remotes.append(make_remote(name, client))
                else:
                    if verbose:
                        print(f"Found strange device: {device}")

            groups = await bridge.get_groups()
            group_devices = {}
            for g in groups:
                group_devices[g["friendly_name"]] = make_bulb(g["friendly_name"], client)
           
            
            all_lights = make_bulb("all_lights",client)
            async with MultiACM(remotes+lights):
                await main(MonadenKit(remotes, lights, all_lights, group_devices))

