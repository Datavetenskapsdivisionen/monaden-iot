from typing import Literal, LiteralString
from dataclasses import dataclass

primetive_tuple = None | int | str |float | tuple[int, str | int, float | str, float | int, str, float]
@dataclass
class Category[data_type: primetive_tuple]:
    data: data_type

class Volume(Category[float]):
    pass
class VolumeUp(Category[None]):
    data = None
class VolumeDown(Category[None]):
    data = None
class Play(Category[None]):
    data = None
class Pause(Category[None]):
    data = None
class Toggle_play_pause(Category[None]):
    pass
class QueueNext(Category[None]):
    data = None
class QueuePrevious(Category[None]):
    data = None
