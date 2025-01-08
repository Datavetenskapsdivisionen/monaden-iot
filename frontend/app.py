import multiprocessing.context
import multiprocessing.pool
import multiprocessing.queues
import multiprocessing.sharedctypes
import os
import sys
import signal
import time

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))


from typing import Tuple, Callable
from flask import Flask, request, redirect, url_for, render_template
from backend.aiomqtt_imp import run_with_monaden_kit, MonadenKit
from backend.Devices import IkeaColorLight
import asyncio
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import argparse
import pychromecast


parser = argparse.ArgumentParser()
parser.add_argument('--host', type=str,default="localhost")
parser.add_argument('--port', type=int, default=5000)
parser.add_argument('--backend_host', type=str,default="localhost")
parser.add_argument('--backend_port', type=int, default=1883)
parser.add_argument('--backend_prefix', type=str,default="zigbee2mqtt")
args = parser.parse_args()

app = Flask(__name__)
HOST = args.host
PORT = args.port
BACKEND_HOST = args.backend_host
BACKEND_PORT = args.backend_port
BACKEND_PREFIX = args.backend_prefix

lamp_T = Tuple[int, Tuple[int, int, int]]
light_changes: multiprocessing.queues.Queue[lamp_T] = multiprocessing.Queue()
volume_changed: multiprocessing.queues.Queue[float] = multiprocessing.Queue()


async def mp2async[*args,ret](func: Callable[[*args],ret], args: Tuple[*args]) -> ret:
    loop = asyncio.get_running_loop()   
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, func, *args)
    return result





async def main(kit: MonadenKit):
    global changes
    await kit.all_lights.set_state("OFF")
    await kit.all_lights.set_state("ON")
    await asyncio.sleep(0.5)
    try:
        while True: 
            brightness, (r,g,b) = await mp2async(light_changes.get,())
            print((brightness, (r,g,b)))
            
            await kit.all_lights.set_brightness(brightness)
            await kit.all_lights.set_color(IkeaColorLight.ColorRGB(r,g,b))
    except KeyboardInterrupt:
        print("Shuting down backend")


def main_sync_wrapper(verbose: bool = False):

    asyncio.run(run_with_monaden_kit(main,BACKEND_HOST,BACKEND_PORT, BACKEND_PREFIX,
                                                 verbose))
   

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/light', methods=['POST'])
def light():
    print("light started")
    color: str | None = request.form.get('color')
    dimmer: str | None  = request.form.get('dimmer')
    print("adafscad", request.form)
    if color != None and dimmer != None:
        r = int(color[1:3], base=16)
        g = int(color[3:5], base=16)
        b = int(color[5:], base=16)
        #print(f'Color: {color}, Dimmer: {dimmer}')
        light_changes.put((int(dimmer), (r,g,b)))
    if 'action' in request.form:
        print("action!")
        action = request.form['action']
        # Handle the button presses here
        if action == 'turn_on':
            light_changes.put((255, (255, 255, 255)))
        elif action == 'turn_off':
            light_changes.put((0, (0,0,0)))
        
    return redirect(url_for('index'))

@app.route('/sound', methods=['POST'])
def sound():
    print(dict(request.form))
    volume: str | None  = request.form.get('volume')
    print(f"volume got!{volume}")
    if volume == None:
        return redirect(url_for('index'))
    volume_changed.put(int(volume) / 1000)
    return redirect(url_for('index'))

def sound_main():
    chromecast = pychromecast.get_listed_chromecasts(friendly_names=["Living Room TV"])[0][0]
    chromecast.wait()
    while True:
        new_volume = volume_changed.get()
        print(f"volume gotten! {new_volume}")
        chromecast.set_volume(new_volume)
        time.sleep(0.1)
        

def worker[*args_T](func: Callable[[*args_T],None], args: Tuple[*args_T]):
    try:
        func(*args)
    except Exception as e:
        print(e)



if __name__ == '__main__':

    frontend_process = multiprocessing.Process(target=app.run, args=(HOST, PORT), name="---FRONTEND---")
    light_process = multiprocessing.Process(target=main_sync_wrapper, args=(False, ), name="---LIGHTS---")
    sound_process = multiprocessing.Process(target=sound_main, name="---SOUND---")
    try:
        frontend_process.start()
        light_process.start()
        sound_process.start()
        frontend_process.join()
        light_process.join()
        sound_process.join()


    except Exception:
        frontend_process.terminate()
        light_process.terminate()
        sound_process.terminate()
        print("---ALL PROCESSES KILLED---")
    
