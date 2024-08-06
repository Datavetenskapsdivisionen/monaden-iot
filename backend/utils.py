from typing import Generic, TypeVar, List, Dict, Callable, Any, Coroutine
import asyncio
from asyncio import Task

load_type = TypeVar("load_type")
class Load_limiter(Generic[load_type]):
    def __init__(self, objects: List[load_type], 
                 object_min_rest: float,            #the minimum time bwteen acceses on indeviudal objects
                 network_max_load: int,             #subable_Tmax number of accesses on the network
                 network_load_time: float           #the duration of a network access
                 ) -> None:
                
        self.object_min_rest = object_min_rest 
         
        self.network_load_time = network_load_time 
        self.network_locks: asyncio.Semaphore = asyncio.Semaphore(network_max_load)
        self.object_locks: Dict[load_type, asyncio.Lock]= {
            l:asyncio.Lock() for l in objects}
     
        self.task_shield: set[Task[None]] = set()  # Prevent tasks from disappearing



   
    
    


        
    async def acces(self, object: load_type):
        object_lock = self.object_locks[object]
        await object_lock.acquire() #Aquire object
        await self.network_locks.acquire()


        #Takes a network capacity spot for network_load_time seconds
        async def callback_in_time(time: float, func: Callable[[], Any] ):
            await asyncio.sleep(time)
            result = func()
            if type(result) == Coroutine:
                await result
        object_lock.release()
        release_object = asyncio.create_task(
            callback_in_time(self.object_min_rest, object_lock.release))
        release_network = asyncio.create_task(
            callback_in_time(self.network_load_time, self.network_locks.release))
        
        self.task_shield.add(release_object)
        release_object.add_done_callback(self.task_shield.discard)
        self.task_shield.add(release_network)
        release_network.add_done_callback(self.task_shield.discard)
        