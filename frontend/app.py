import multiprocessing.queues
import os
import sys
import time

sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))

import pychromecast
from typing import Tuple, Callable, List, Literal, Any, Dict, Coroutine
from flask import Flask, request, redirect, url_for, render_template
from flask_socketio import SocketIO
from backend.aiomqtt_imp import run_with_monaden_kit, MonadenKit
from backend.Devices import IkeaColorLight
from backend import Chromecast
import asyncio
import multiprocessing
import ctypes
from concurrent.futures import ThreadPoolExecutor
import argparse
from backend.Devices import IKEA_tradfri_remote_action_type

parser = argparse.ArgumentParser()
parser.add_argument('--host', type=str,default="localhost")
parser.add_argument('--port', type=int, default=5000)
parser.add_argument('--backend_host', type=str,default="localhost")
parser.add_argument('--backend_port', type=int, default=1883)
parser.add_argument('--backend_prefix', type=str,default="zigbee2mqtt")
parser.add_argument('--debug', type=bool,default=False)
args = parser.parse_args()

app = Flask(__name__)
socketio = SocketIO(app)

HOST = args.host
PORT = args.port
BACKEND_HOST = args.backend_host
BACKEND_PORT = args.backend_port
BACKEND_PREFIX = args.backend_prefix
DEBUG = args.debug



lamp_T = Tuple[int, Tuple[int, int, int]]
light_changes: multiprocessing.queues.Queue[lamp_T] = multiprocessing.Queue()





chromecast_changed: multiprocessing.queues.Queue[Chromecast.Category[Any]] = multiprocessing.Queue()

chromecast_idel_status = multiprocessing.Value(ctypes.c_bool, False)
chromecast_app = multiprocessing.Value(ctypes.c_char_p, "none".encode())
color_wheel_t = Literal["red", "blue", "purple"]
color_wheel: Dict[color_wheel_t, IkeaColorLight.ColorRGB] = {
    "red": IkeaColorLight.ColorRGB(256, 0, 0),
    "blue":  IkeaColorLight.ColorRGB(0, 0, 256),
    "purple": IkeaColorLight.ColorRGB(206, 0, 252)
}
async def sleep_then_do[*args,ret](
    seconds: float, 
    func: Callable[[*args], Coroutine[Any, Any, ret]], 
     args: Tuple[*args] = ()
) -> ret:
    await asyncio.sleep(seconds)
    return await func(*args)

async def remote_action_handelers_for_cc_sound(action: IKEA_tradfri_remote_action_type):

    match action:
        case "arrow_left_click":
            pass
        case "arrow_left_hold":
            await mp2async(chromecast_changed.put, (Chromecast.QueuePrevious(None), ))
        case "arrow_left_release":
            pass
        case "arrow_right_click":
            pass
        case "arrow_right_hold":
            await mp2async(chromecast_changed.put, (Chromecast.QueueNext(None), ))
        case "arrow_right_release":
            pass
        case "brightness_down_click":
            await mp2async(chromecast_changed.put, (Chromecast.VolumeDown(None), ))
        case "brightness_down_hold":
            await mp2async(chromecast_changed.put, (Chromecast.Volume(0), ))
        case "brightness_down_release":
            pass
        case "brightness_up_click":
            await mp2async(chromecast_changed.put, (Chromecast.VolumeUp(None), ))
        case "brightness_up_hold":
            await mp2async(chromecast_changed.put, (Chromecast.VolumeUp(None), ))
        case "brightness_up_release":
            pass
        case "toggle":
            await mp2async(chromecast_changed.put, (Chromecast.Toggle_play_pause(None), ))
        case "toggle_hold":
            pass

def register_remote_action_handelers_for_IKEA_lights(all_lights: IkeaColorLight):
    current_collor:color_wheel_t = "red"
    async def remote_action_handelers_for_IKEA_lights(action: IKEA_tradfri_remote_action_type):
        print("handeld light action")
        nonlocal current_collor 
        match action:
            case "arrow_left_click":
                keys = list(color_wheel.keys())
                current_collor = keys[(keys.index(current_collor) - 1) % len(color_wheel.keys())]
                await all_lights.set_color(color_wheel[current_collor])
            case "arrow_left_hold":
                pass
            case "arrow_left_release":
                pass
            case "arrow_right_click":
                keys = list(color_wheel.keys())
                current_collor = keys[(keys.index(current_collor) + 1) % len(color_wheel.keys())]
                await all_lights.set_color(color_wheel[current_collor])
            case "arrow_right_hold":
                pass
            case "arrow_right_release":
                pass
            case "brightness_down_click":
                await all_lights.step_brightness(-20)
            case "brightness_down_hold":
                await all_lights.set_brightness(10)
            case "brightness_down_release":
                pass
            case "brightness_up_click":
                await all_lights.step_brightness(20)
            case "brightness_up_hold":
                await all_lights.step_brightness(254)
            case "brightness_up_release":
                pass
            case "toggle":
                await all_lights.set_state("TOGGLE")
            case "toggle_hold":
                pass
    remote_action_handelers["lights"] = remote_action_handelers_for_IKEA_lights
remote_mode_type = Literal["sound", "lights"]
remote_mode_changes: multiprocessing.queues.Queue[remote_mode_type] = multiprocessing.Queue()
remote_action_handelers: Dict[remote_mode_type, Callable[[IKEA_tradfri_remote_action_type], Coroutine[Any, Any, None]]] = {
    "sound": remote_action_handelers_for_cc_sound
}


async def mp2async[*args,ret](func: Callable[[*args],ret], args: Tuple[*args] = ()) -> ret:
    loop = asyncio.get_running_loop()   
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, func, *args)
    return result

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_chromecast_idel_status')
def update_chromecast_idel_status():
    return render_template("chromecast.html", 
                           status=  "active" if chromecast_idel_status.value else "idel", 
                           app=b"" if chromecast_app.value == None else chromecast_app.value.decode())

@app.route('/light', methods=['POST'])
def light():
    color: str | None = request.form.get('color')
    dimmer: str | None  = request.form.get('dimmer')
    if color != None and dimmer != None:
        r = int(color[1:3], base=16)
        g = int(color[3:5], base=16)
        b = int(color[5:], base=16)
        light_changes.put((int(dimmer), (r,g,b)))
        print(f"put {(int(dimmer), (r,g,b))}")
    if 'action' in request.form:
        action = request.form['action']
        # Handle the button presses here
        if action == 'turn_on':
            light_changes.put((255, (255, 255, 255)))
        elif action == 'turn_off':
            light_changes.put((0, (0,0,0)))
        
    return redirect(url_for('index'))

@app.route('/sound', methods=['POST'])
def sound():
    volume: str | None  = request.form.get('volume')
    command: str |None = request.form.get('command')
    if command != None:
        if command == "previous":
            chromecast_changed.put(Chromecast.QueuePrevious(None))
        elif command == "play":
            chromecast_changed.put(Chromecast.Play(None))
        elif command == "pause":
            chromecast_changed.put(Chromecast.Pause(None))
        elif command == "next":
            chromecast_changed.put(Chromecast.QueueNext(None))
    elif volume != None:
        chromecast_changed.put(Chromecast.Volume(int(volume) / 1000))
    return redirect(url_for('index'))

"""@app.route('/controller_mode', methods=['POST'])
def sound():
    mode: str | None  = request.form.get('mode')
    if isinstance(mode, remote_mode_type):
        remote_mode_changes.put(mode)
    else:
        print(f"Wrong mode string, got: {mode}")
    return redirect(url_for('index'))
"""

def zigbee_main(verbose: bool = False):
    async def main(kit: MonadenKit):
        controller_mode: remote_mode_type = "lights"
        await kit.all_lights.set_state("OFF")
        await kit.all_lights.set_state("ON")
        await asyncio.sleep(0.5)
        register_remote_action_handelers_for_IKEA_lights(kit.all_lights)
        print("????")
        async def lights():
            while True:
                 
                brightness, (r,g,b) = await mp2async(light_changes.get)
                print("got this from light_changes", (brightness, (r,g,b)))
                await kit.all_lights.set_brightness(brightness)
                await kit.all_lights.set_color(IkeaColorLight.ColorRGB(r,g,b))
        async def controller_mode_listener(controller_mode: remote_mode_type):
            while True:
                controller_mode = await mp2async(remote_mode_changes.get)
        async def controller(controller_mode: remote_mode_type):
            remote = kit.TRADFRI_remotes[0]
            toggle_task: asyncio.Task[None] | None = None
            while True:
                action = await remote.get_action()
                if action == "toggle":
                    if toggle_task != None and not toggle_task.done():
                        toggle_task.cancel()
                        print("got double toggle")
                        keys = list(remote_action_handelers.keys())
                        controller_mode = keys[(keys.index(controller_mode) + 1) % len(remote_action_handelers.keys())]
                        print(f"Switched controller mode to: {controller_mode}")
                    else:
                        print("got toggle")
                        toggle_task = asyncio.Task(sleep_then_do(0.3,remote_action_handelers[controller_mode], (action,)))
                    continue
                print("got from controller:", action)
                await remote_action_handelers[controller_mode](action)

        
        await asyncio.gather(lights(), controller(controller_mode))

    asyncio.run(run_with_monaden_kit(main,BACKEND_HOST,BACKEND_PORT, BACKEND_PREFIX,
                                                 verbose))
   

def chromecast_main():
    global chromecast_idel_status 
    global chromecast_app
    cc = pychromecast.get_listed_chromecasts(friendly_names=["Monaden CC"])[0][0]
    cc.wait()
    class ML(pychromecast.controllers.media.MediaStatusListener):
        def __init__(self) -> None:
            
            self.status: pychromecast.controllers.media.MediaStatus | None = None
            super().__init__()
        def new_media_status(self, status: pychromecast.controllers.media.MediaStatus) -> None:
            self.status = status

        def load_media_failed(self, queue_item_id: int, error_code: int) -> None:
            pass
    
    class SL(pychromecast.controllers.receiver.CastStatusListener):
        def __init__(self) -> None:
            self.status: None | pychromecast.controllers.receiver.CastStatus = None
            super().__init__()
        def new_cast_status(self, status: pychromecast.controllers.receiver.CastStatus) -> None:
            self.status = status
 
    ml = ML()
    cc.media_controller.register_status_listener(ml)
    sl = SL()
    cc.register_status_listener(sl)
    
    while True:
        cc_chnage = chromecast_changed.get()
        print("recived: ", type(cc_chnage))
        print(ml.status == None, sl.status == None)
        if ml.status != None:
            match type(cc_chnage):
                case Chromecast.Volume:
                    
                    cc.set_volume(cc_chnage.data)
                case Chromecast.QueueNext:
                    print("q next")
                    if ml.status.supports_queue_next:
                        print("queued")
                        cc.media_controller.queue_next()
                case Chromecast.QueuePrevious:
                    if ml.status.supports_queue_next:
                        cc.media_controller.queue_next()
                case Chromecast.VolumeUp:
                    cc.volume_up()
                case Chromecast.VolumeDown:
                    cc.volume_down()
                case Chromecast.Toggle_play_pause:
                    if ml.status.player_is_paused:
                        cc.media_controller.play()
                    elif ml.status.supports_pause:
                        cc.media_controller.pause()
                case Chromecast.Play:
                    cc.media_controller.play()
                case Chromecast.Pause:
                   if ml.status.supports_pause:
                        cc.media_controller.pause() 
        #chromecast.media_controller.skip(0)
        time.sleep(0.1)


def flask_main():
    app.run(HOST, PORT)

if __name__ == '__main__':
    processes: List[multiprocessing.Process] = []
    processes.append(multiprocessing.Process(target=(flask_main), name="---FRONTEND---"))
    processes.append(multiprocessing.Process(target=(zigbee_main), args=(DEBUG, ), name="---LIGHTS---"))
    processes.append(multiprocessing.Process(target=(chromecast_main), name="---chromeCAST---"))
    try:
        [p.start() for p in processes]
        [p.join() for p in processes]
        print("ALL PROCESSES JOINED")
    except BaseException:
        print("---TERMENATING ALL PROCESSES---")
        [p.terminate() for p in processes]
        print("---ALL PROCESSES TERMINATED---")
    
