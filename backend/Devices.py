from typing import Protocol, Literal, Any
from dataclasses import dataclass


class IkeaColorLight(Protocol):
  
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...
    
    @dataclass
    class ColorXY:
        x: float #0 to 1
        y: float #0 to 1
    @dataclass
    class ColorRGB:
        r: int #0 to 254
        g: int #0 to 254
        b: int #0 to 254

 
        

    
    async def set_state(self, state: Literal["ON", "OFF", "TOGGLE"], 
                  on_time: int | None = None, #posetive
                  off_wait_time: int | None = None): #posetive
        ...
    async def get_state(self) -> Literal["ON", "OFF", "TOGGLE"]:
        ...
    async def set_brightness(self, brightness: int, #0 to 254
                       transition: int | None = None): #posetive
        ...
    async def get_brightness(self) -> int:
        ...
    async def move_brightness(self, speed: int | Literal["stop"]): #-254 to 254
        ...
    async def step_brightness(self, step_size: int): #-254 to 254
        ...
    async def set_color_temp(self, color_temp: int): #153 to 500
        ...
    async def get_color_temp(self) -> int:  #153 to 500
        ...
    async def set_color_temp_startup(self, color_temp_startup: int):#153 to 500
        ...
    async def set_color(self, color: ColorXY | ColorRGB,
                       transition: int | None = None):
        ...
    async def get_color(self) -> ColorRGB:
        ...
    async def move_color(self, speed: int | Literal["stop"]): #-254 to 254
        ...
    async def step_color(self, step_size: int): #-254 to 254
        ...
    
    async def set_effect(self, effect: Literal["blink","breathe","okay","channel_change", "finish_effect" ,"stop_effect", "colorloop", "stop_colorloop"]):
        ...
    async def set_power_on_behavior(self, behavior: Literal["off", "on", "toggle", "previous"]):
        ...
    async def get_power_on_behavior(self) -> Literal["off", "on", "toggle", "previous"]:
        ...
    async def set_allow_color_and_temperature_while_off(self, b: bool):
        ...
    async def get_allow_color_and_temperature_while_off(self) -> bool:
        ...

IKEA_tradfri_remote_action_type = Literal["toggle", 
                                    "brightness_up_click", 
                                    "brightness_down_click", 
                                    "brightness_up_hold", 
                                    "brightness_up_release", 
                                    "brightness_down_hold",
                                    "brightness_down_release", 
                                    "toggle_hold", 
                                    "arrow_left_click", 
                                    "arrow_left_hold", 
                                    "arrow_left_release", 
                                    "arrow_right_click", 
                                    "arrow_right_hold", 
                                    "arrow_right_release"]
class IKEA_tradfri_remote(Protocol):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        ...
    async def get_action(self) -> IKEA_tradfri_remote_action_type:
        ...
    async def get_battery_now(self) -> int:
        ...
    async def get_battery(self) -> int:
        ...



