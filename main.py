
from DevOri.Aiomqtt_imp import make_deviceClient
from backend.aiomqtt_imp import MonadenKit, run_with_monaden_kit, make_bridge, make_bulb
import os
import asyncio
from DevOri.utils import any2bytes, LambdaSubscriber
from backend.Devices import IkeaColorLight
from aiomqtt import Message as Aiomessage
from backend.Devices import IkeaColorLight
from random import randint
from typing import Tuple, Callable
from SoundAnalysis.beatFinder import PyAudioBF, BeatFinder
import time
from pynput import keyboard
import sys
import random

from aiotools import TaskGroup # type: ignore has no stubs

PREFIX = "zigbee2mqtt"
HOST = os.environ.get("MQTT_ADDR", "localhost")
PORT = 1883

def sort_lights(lights):
    return [lights[0], lights[8], lights[12],lights[5], lights[3], lights[9], lights[11], lights[7], lights[1], lights[4], lights[10], lights[6], lights[2]]

async def start(kit: MonadenKit, color: Tuple[int, int, int] = (255, 255, 255)):
    kit.lights = sort_lights(kit.lights)
    await kit.all_lights.set_state("ON")
    await kit.all_lights.set_allow_color_and_temperature_while_off(True)
    await asyncio.sleep(1)
    await kit.all_lights.set_color(IkeaColorLight.ColorRGB(*color))
    await asyncio.sleep(1)
    await kit.all_lights.set_state("OFF")
    await asyncio.sleep(1)
    await kit.all_lights.set_state("ON")
    await asyncio.sleep(1)
    await kit.all_lights.set_brightness(0)
    await asyncio.sleep(1)

async def main(kit: MonadenKit):
    await start(kit)

    while True:
        
        await kit.lights[2].set_brightness(2)
        await asyncio.sleep(0.1)
        await kit.lights[2].set_brightness(100)
        await asyncio.sleep(0.1)

async def all_blink(kit: MonadenKit): 
    await kit.all_lights.set_color_temp(0)
    await asyncio.sleep(1)
    await kit.all_lights.set_state("OFF")
    await asyncio.sleep(1)
    await kit.all_lights.set_state("ON")
    await asyncio.sleep(1)
    
    while True:
        await kit.all_lights.set_brightness(100)
        await asyncio.sleep(0.1)
        await kit.all_lights.set_brightness(0)
        await await_keypress()

async def runner(kit: MonadenKit):

    async def set_after(light: IkeaColorLight, level: int, after: float):
        await asyncio.sleep(after)
        await light.set_brightness(level)


    miin = 0
    maax = 80

    up_time = 0.1
    down_time = 0.3
    
    



    await start(kit, color=(0,0,254))

    

    await kit.all_lights.set_brightness(miin)
    a = 0
    s = time.time()
    size = 3
    time_out = list(kit.lights[:size])
    time_in = list(kit.lights[size:])
    async with TaskGroup() as tg:
        while True:
            
            l = random.choice(time_in)
            #await kit.lights[i].set_color(IkeaColorLight.ColorRGB(randint(0,255), randint(0,255), randint(0,255)))
            e = time.time()  
            await l.set_brightness(maax)
            tg.create_task(set_after(l, miin, up_time))
            time_in.remove(l)
            time_out.append(l)
            l2 = time_out[0]
            time_out.remove(l2)
            time_in.append(l2)
            await asyncio.sleep(down_time)

            
            
            
        
async def invert_runner(kit: MonadenKit):
    await start(kit, color=(0,0,254))
    await kit.all_lights.set_brightness(0)
    while True:
        for l in kit.lights:
            await l.set_brightness(100)
            await asyncio.sleep(0.3)
            await l.set_brightness(0)

async def tvatakt(kit: MonadenKit):
    
    miin = 1
    maax = 180

    
    down_time = 0.3

    await start(kit, color=(0,0,254))    
    
    while True:
        await kit.lights[6].set_brightness(maax)
        await kit.lights[5].set_brightness(maax)
        await kit.lights[6].set_brightness(miin)
        await kit.lights[5].set_brightness(miin)
        await await_keypress()
        
        await kit.lights[0].set_brightness(maax)
        await kit.lights[-1].set_brightness(maax)
        await kit.lights[0].set_brightness(miin)
        await kit.lights[-1].set_brightness(miin)
        await await_keypress()

import curses

async def await_keypress():
    return await asyncio.to_thread(curses.wrapper, get_keypress)
def get_keypress(stdscr):
    # Wait for a single key press
    return stdscr.getch()
async def manual_tvatakt(kit: MonadenKit):
    miin = 1
    maax = 200

    
    down_time = 0.3

    await start(kit)    
    



    while True:
        await kit.lights[6].set_brightness(maax)
        await kit.lights[5].set_brightness(maax)
        await kit.lights[0].set_brightness(miin)
        await kit.lights[-1].set_brightness(miin)
        await await_keypress()
        
        await kit.lights[6].set_brightness(miin)
        await kit.lights[5].set_brightness(miin)
        await kit.lights[0].set_brightness(maax)
        await kit.lights[-1].set_brightness(maax)
        await await_keypress()
     

async def main2(): 

    async with make_deviceClient(HOST,
                             PORT,
                             PREFIX,
                             verbose=False) as client:
        async with make_bridge(client) as bridge:   
            #a = await bridge.get_from beat_detector_pipable import agroups()
            #g_name = a[0]["friendly_name"]
            
            groups = await bridge.get_groups()
            d_name = groups[2]["friendly_name"]
            while True:
                await client.send(f"{d_name}/set", any2bytes({"brightness": 2}))
                await asyncio.sleep(0.3)
                await client.send(f"{d_name}/set", any2bytes({"brightness": 100}))
                await asyncio.sleep(0.3)

def start_beat_finder(call_back: Callable[[float], None]) -> PyAudioBF:
    sample_rate = 200000
    bf = BeatFinder(call_back, sample_rate, 
                    base_frequency_cutoff=1000,
                    lookback_window_length=3)
    isbf = PyAudioBF(bf, 0.1, sample_rate)
    isbf.start()
    return isbf
            
async def music_sync(kit: MonadenKit):
    await start(kit)


    queue: asyncio.queues.Queue[float] = asyncio.Queue()
    isbf = start_beat_finder(lambda prob: queue.put_nowait(prob))
    threashold = 0.7
    down_time = 0.4
    beat = False
    before = time.time()
    print("start")
    i = 0
    while True:
        prob = await queue.get()
        print("got")
        await asyncio.sleep(max(0, down_time + before - time.time()))
        if (not beat) and prob > threashold:
            print("up")
            beat = not beat
            await kit.all_lights.set_brightness(100)
        elif beat and prob <= threashold:
            beat = not beat
            await kit.all_lights.set_brightness(5)
            print("up")
        else:
            print("none")
        before = time.time()
        while not queue.empty():
            await queue.get()
            i += 1
        print("empty")
        i += 1
        print(i)


async def octoberfest(kit: MonadenKit):
    await start(kit)
    await kit.all_lights.set_brightness(100)
    white = (255,255,255)
    blue = (0, 102, 204)
    wait_time = 2.5
    
    even = [l for i, l in enumerate(kit.lights) if i%2 == 0]
    odd = [l for i, l in enumerate(kit.lights) if i%2 == 1]

    while True: 
        for l in even:
            await l.set_color(IkeaColorLight.ColorRGB(*white))
        for l in odd:
            await l.set_color(IkeaColorLight.ColorRGB(*blue))
        await asyncio.sleep(wait_time)
        for l in even:
            await l.set_color(IkeaColorLight.ColorRGB(*blue))
        for l in odd:
            await l.set_color(IkeaColorLight.ColorRGB(*white))
        await asyncio.sleep(wait_time)

async def glögkväll(kit: MonadenKit):
    await start(kit)
    await kit.all_lights.set_brightness(100)
    white = (228, 0, 16)
    blue = (0, 102, 14)
    wait_time = 10
    
    even = [l for i, l in enumerate(kit.lights) if i%2 == 0]
    odd = [l for i, l in enumerate(kit.lights) if i%2 == 1]

    while True: 
        for l in even:
            await l.set_color(IkeaColorLight.ColorRGB(*white))
        for l in odd:
            await l.set_color(IkeaColorLight.ColorRGB(*blue))
        await asyncio.sleep(wait_time)
        for l in even:
            await l.set_color(IkeaColorLight.ColorRGB(*blue))
        for l in odd:
            await l.set_color(IkeaColorLight.ColorRGB(*white))
        await asyncio.sleep(wait_time)
   
if __name__ == "__main__":  
    asyncio.run(run_with_monaden_kit(glögkväll,HOST,PORT,PREFIX,verbose=False))
    #asyncio.run(main2())
   