import multiprocessing.queues
import os
import sys
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))


from typing import Tuple, Callable
from flask import Flask, request, redirect, url_for, render_template
from backend.aiomqtt_imp import run_with_monaden_kit, MonadenKit
from backend.Devices import IkeaColorLight
import asyncio
import multiprocessing
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
PREFIX = "zigbee2mqtt"
HOST = os.environ.get("MQTT_ADDR", "localhost")
PORT = 1883
lamp_T = Tuple[int, Tuple[int, int, int]]
changes: multiprocessing.queues.Queue[lamp_T] = multiprocessing.Queue()


async def mp2async[*args,ret](func: Callable[[*args],ret], args: Tuple[*args]) -> ret:
    loop = asyncio.get_running_loop()   
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, func, *args)
    return result

async def main(kit: MonadenKit):
    global changes
    
    try:
        while True: 
            changes.get
            brightness, (r,g,b) = await mp2async(changes.get,())
            print((brightness, (r,g,b)))
            for light in kit.lights:
                await light.set_brightness(brightness)
                await light.set_color(IkeaColorLight.ColorRGB(r,g,b))
    except KeyboardInterrupt:
        print("Shuting down backend")


def main_sync_wrapper(verbose: bool = False):

    asyncio.run(run_with_monaden_kit(main,HOST,PORT, PREFIX,
                                                 verbose))
   

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def submit():
   
    color: str | None = request.form.get('color')
    dimmer: str | None  = request.form.get('dimmer')
    print("adafscad", request.form)
    if color != None and dimmer != None:
        r = int(color[1:3], base=16)
        g = int(color[3:5], base=16)
        b = int(color[5:], base=16)
        #print(f'Color: {color}, Dimmer: {dimmer}')
        changes.put((int(dimmer), (r,g,b)))
    if 'action' in request.form:
        print("action!")
        action = request.form['action']
        # Handle the button presses here
        if action == 'turn_on':
            changes.put((255, (255, 255, 255)))
        elif action == 'turn_off':
            changes.put((0, (0,0,0)))
        
    return redirect(url_for('index'))



if __name__ == '__main__':
    print("host__", HOST)
    main_process = multiprocessing.Process(target=main_sync_wrapper, args= [False])
    main_process.start()
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        pass
    print("Shuting down all")
    main_process.terminate()
   
    