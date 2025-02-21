from typing import Callable, Literal, Dict, Any, List, LiteralString, Type
from .Devices import IkeaColorLight, IKEA_tradfri_remote, IKEA_tradfri_remote_action_type
from DevOri.mqttDevices import Device, Communicator
from DevOri.utils import bytes2any 
from enum import Enum, auto

class Zigbee2mqttDevice[send_T, valid_send_topics: LiteralString, receive_T, valid_recive_topics: LiteralString, e: Enum](
    Device[send_T, valid_send_topics, receive_T, valid_recive_topics, e]):
    def __init__(self, friendly_name: str, 
                 communicator: Communicator[send_T, receive_T], 
                 category_sorters: Dict[Any, Callable[[receive_T], Any]], 
                 categories: type, 
                 dict2send_T: Callable[[Dict[str, Any]], send_T],
                 recive_T2dict: Callable[[receive_T], Dict[str, Any]],
                 message_save_limit: Dict[Any, Dict[Any, int]] = {}, 
                 prefix: str = "") -> None:
        self._dict2send_T = dict2send_T
        self._recive_T2dict = recive_T2dict
        super().__init__(friendly_name, 
                         communicator, 
                         category_sorters, 
                         categories, 
                         message_save_limit, 
                         prefix)
    async def send_to_dict(self, topic: valid_send_topics, payload: Dict[str, Any]):
        p = self._dict2send_T(payload)
        await super().send_to(topic, p)



    async def recive_from_dict(self, topic: valid_recive_topics, category: e) -> Dict[str, Any]:
        return self._recive_T2dict(await super().recive_from(topic, category))

SET = "set"
GET = "get"
READ = ""

class GetKinds(Enum):
    STATE = auto()
    BRIGHTNESS = auto()
    COLORTEMP = auto()
    COLOR = auto()
    POWERONBEHAVIOR = auto()
    ALLOWSETTEMPCOLORWHILEOFF = auto()

#https://www.zigbee2mqtt.io/devices/LED1925G6.html
message_T = Dict[str, str | int | float]
class IkeaColorLight_devori[send_T, recive_T](Zigbee2mqttDevice[send_T, Literal["set", "get"], recive_T, Literal[""], GetKinds], IkeaColorLight):
    
    def __init__(self, friendly_name: str,
                 communicator: Communicator[send_T, recive_T],
                 sort_gets: Callable[[recive_T], GetKinds],
                 dict2send_T: Callable[[Dict[str, Any]], send_T],
                 recive_T2dict: Callable[[recive_T], Dict[str, Any]],
                 prefix: str = "",
                 ) -> None:
        super().__init__(
            friendly_name=friendly_name,
            communicator=communicator,
            category_sorters={"": sort_gets}, 
            categories=GetKinds,
            dict2send_T=dict2send_T,
            recive_T2dict=recive_T2dict,
            prefix=prefix
            )
    

    async def set_state(self, state: Literal["ON", "OFF", "TOGGLE"], 
                  on_time: int | None = None, #posetive
                  off_wait_time: int | None = None): #posetive
        d: Dict[str, Any] = {"state": state}
        if state == "ON":
            if on_time != None:
                d["on_time"] = on_time
            if off_wait_time != None:
                d["off_wait_time"] = off_wait_time
            
        await self.send_to(SET, self._dict2send_T(d))

    async def get_state(self) -> Literal["ON", "OFF", "TOGGLE"]:
        await self.send_to_dict(GET, {"state": ""})
        message = await self.recive_from_dict(READ, GetKinds.STATE)
        state = message["state"]
        if state == "ON":
            return "ON"
        elif state == "OFF":
            return "OFF"
        elif state == "TOGGLE":
            return "TOGGLE"
        raise Exception("Intrnal error") 
    async def set_brightness(self, brightness: int, #0 to 254
                       transition: int | None = None): #posetive
        
        d = {"brightness": brightness}
        if transition != None:
            d["transition"] = transition
        await self.send_to_dict(SET,d)
    async def get_brightness(self) -> int:
        await self.send_to_dict(GET,{"brightness": ""})
        message = await self.recive_from_dict(READ, GetKinds.STATE)
        i: int = message["brightness"] 
        return i
                
    async def move_brightness(self, speed: int | Literal["stop"]): #-254 to 254
        await self.send_to_dict(SET,{"brightness_move": speed})

    async def step_brightness(self, step_size: int): #-254 to 254
        await self.send_to_dict(SET, {"brightness_step": step_size})

    async def set_color_temp(self, color_temp: int): #153 to 500
        await self.send_to_dict(SET, {"color_temp": color_temp})
        
    async def get_color_temp(self) -> int:  #153 to 500
        await self.send_to_dict(SET, {"color_temp": ""})
        message = await self.recive_from_dict("", GetKinds.COLORTEMP)
        i: int = message["color_temp"]
        return i
        
    async def set_color_temp_startup(self, color_temp_startup: int):#153 to 500
        await self.send_to_dict(SET, {"color_temp_startup": color_temp_startup})

    async def set_color(self, color: IkeaColorLight.ColorXY | IkeaColorLight.ColorRGB, transition: int | None = None):
        if type(color) == IkeaColorLight.ColorXY:
            payload = {"x": color.x, "y": color.y}
            d: Dict[str, Any] = {"color": payload}
            if transition != None:
                d["transition"] = transition
            await self.send_to_dict(SET, d)
        elif type(color) == IkeaColorLight.ColorRGB:
            payload = {"rgb": f"{color.r},{color.g},{color.b}"}
            await self.send_to_dict(SET, {"color": payload})
        else:
            raise Exception(f"Color type not suported: {type(color)}") 
        
    async def get_color(self) -> IkeaColorLight.ColorRGB:
        await self.send_to_dict(GET,{"color":{"r": "", "g": "", "b": ""}})
        message = await self.recive_from_dict("", GetKinds.COLOR)
        d = message["color"] 
        return IkeaColorLight.ColorRGB(d["r"], d["g"],d)
    async def move_color(self, speed: int | Literal["stop"]): #-254 to 254
        await self.send_to_dict(SET, {"color_temp_move": speed})
    async def step_color(self, step_size: int): #-254 to 254
        await self.send_to_dict(SET,{"color_temp_step": step_size})
    async def set_effect(self, effect: Literal["blink","breathe","okay","channel_change", "finish_effect" ,"stop_effect", "colorloop", "stop_colorloop"]):
        await self.send_to_dict(SET, {"effect": effect})
    async def set_power_on_behavior(self, behavior: Literal["off", "on", "toggle", "previous"]):
        await self.send_to_dict(SET, {"power_on_behavior": behavior})
    async def get_power_on_behavior(self) -> Literal["off", "on", "toggle", "previous"]:
        await self.send_to_dict(GET, {"power_on_behavior": ""})
        message = await self.recive_from_dict("", GetKinds.POWERONBEHAVIOR)
        s: str = message["power_on_behavior"] 
        if s == "off":
            return "off"
        elif s == "on":
            return "on"
        elif s == "toggle":
            return "toggle"
        elif s == "previous":
            return "previous"
        raise Exception(f"Internal execption ")
        
    async def set_allow_color_and_temperature_while_off(self, b: bool):
        await self.send_to_dict(SET,{"power_on_behavior": "on" if b else "off"})
        
    async def get_allow_color_and_temperature_while_off(self) -> bool:
        await self.send_to_dict(GET, {"power_on_behavior": ""})
        message = await self.recive_from_dict(READ, GetKinds.ALLOWSETTEMPCOLORWHILEOFF)
        s: str = message["power_on_behavior"] 
        if s == "on":
            return True
        elif s == "off":
            return False
        raise Exception("Internal execption")




class BridgeCategory(Enum):
    ALL = 1




class Bridge[send_T, recive_T](Zigbee2mqttDevice[send_T, Literal["devices", "groups", "request/group/members/add", "request/group/members/remove"],
                                                 recive_T, Literal["devices", "groups"], BridgeCategory]):
    


    def __init__(self, communicator: Communicator[send_T, recive_T], category_sorter: Callable[[recive_T], Any], categories: Type[BridgeCategory], dict2send_T: Callable[[Dict[str, Any]], send_T], recive_T2dict: Callable[[recive_T], Dict[str, Any]], message_save_limit: Dict[Any, Dict[Any, int]] = {}, prefix: str = "") -> None:
        super().__init__("bridge", communicator, {"devices": category_sorter, "groups": category_sorter}, categories, dict2send_T, recive_T2dict, message_save_limit, prefix)
        self._devices: None | List[Dict[str, Any]] = None
        self._groups: None | List[Dict[str, Any]] = None
    
    
    async def get_devices(self) -> List[Dict[str, Any]]:
        if self._devices != None:
            return self._devices
        await self.send_to_dict("devices", {})
        message = await self.recive_from("devices", BridgeCategory.ALL)
        l: List[Dict[str, Any]] = bytes2any(message.payload) # type: ignore
        
        
        self._devices = l
        return l
    
    async def get_groups(self):
        if self._groups != None:
            return self._groups
        await self.send_to_dict("groups", {})
        message = await self.recive_from("groups", BridgeCategory.ALL)
        l: List[Dict[str, Any]] = bytes2any(message.payload) # type: ignore

        self._groups = l
        return l

    async def add_device_to_group(self, device: str, group: str):
        await self.send_to_dict("request/group/members/add", {"group": group, "device": device} )

    async def remove_device_from_group(self, device: str, group: str):
        await self.send_to_dict("request/group/members/remove", {"group": group, "device": device} )
    

    async def __aenter__(self):
        return await super().__aenter__()
    async def __aexit__(self, *exc_info: Any):
        return await super().__aexit__(*exc_info)

    


class RemoteKinds(Enum):
        BATTERYUPDATE = auto()
        ACTION = auto()
#https://www.zigbee2mqtt.io/devices/E1524_E1810.html#ikea-e1524%252Fe1810
class IKEA_tradfri_remote_devori[send_T, recive_T](Zigbee2mqttDevice[send_T, Literal["get"],recive_T, Literal[""], RemoteKinds], IKEA_tradfri_remote):
    
    def __init__(self, friendly_name: str, 
                 communicator: Communicator[send_T, recive_T], 
                 category_sorter:Callable[[recive_T], Any], 
                 categories: Type[RemoteKinds], 
                 dict2send_T: Callable[[Dict[str, Any]], send_T], 
                 recive_T2dict: Callable[[recive_T], Dict[str, Any]], 
                 message_save_limit: Dict[Any, Dict[Any, int]] = {}, 
                 prefix: str = "") -> None:
        super().__init__(friendly_name, communicator, {"": category_sorter}, categories, dict2send_T, recive_T2dict, message_save_limit, prefix)

    

    async def get_action(self) -> IKEA_tradfri_remote_action_type:
        message = await self.recive_from("", RemoteKinds.ACTION)
        d = self._recive_T2dict(message)
        action:str = d["action"]
        if action == "toggle":
            return "toggle"
        elif action == "brightness_up_click":
            return "brightness_up_click"
        elif action == "brightness_down_click":
            return "brightness_down_click"
        elif action == "brightness_up_hold":
            return "brightness_up_hold"
        elif action == "brightness_up_release":
            return "brightness_up_release"
        elif action == "brightness_down_hold":
            return "brightness_down_hold"
        elif action == "brightness_down_release":
            return "brightness_down_release"
        elif action == "toggle_hold":
            return "toggle_hold"
        elif action == "arrow_left_click":
            return "arrow_left_click"
        elif action == "arrow_left_hold":
            return "arrow_left_hold"
        elif action == "arrow_left_release":
            return "arrow_left_release"
        elif action == "arrow_right_click":
            return "arrow_right_click"
        elif action == "arrow_right_hold":
            return "arrow_right_hold"
        elif action == "arrow_right_release":
            return "arrow_right_release"
        raise Exception(f"Internal error, action value: {action}")

    async def get_battery_now(self) -> int:
        d = {"battery": ""}
        await self.send_to("get", self._dict2send_T(d))
        return await self.get_battery()
    
    async def get_battery(self) -> int:
        message = await self.recive_from("", RemoteKinds.BATTERYUPDATE)
        d2 = self._recive_T2dict(message)
        i: int = d2["battery"]
        return i



        