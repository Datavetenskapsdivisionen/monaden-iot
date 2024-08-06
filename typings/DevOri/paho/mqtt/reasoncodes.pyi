"""
This type stub file was generated by pyright.
"""

import functools
from typing import Any

@functools.total_ordering
class ReasonCode:
    """MQTT version 5.0 reason codes class.

    See ReasonCode.names for a list of possible numeric values along with their
    names and the packets to which they apply.

    """
    def __init__(self, packetType: int, aName: str = ..., identifier: int = ...) -> None:
        """
        packetType: the type of the packet, such as PacketTypes.CONNECT that
            this reason code will be used with.  Some reason codes have different
            names for the same identifier when used a different packet type.

        aName: the String name of the reason code to be created.  Ignored
            if the identifier is set.

        identifier: an integer value of the reason code to be created.

        """
        ...
    
    def __getName__(self, packetType, identifier): # -> str:
        """
        Get the reason code string name for a specific identifier.
        The name can vary by packet type for the same identifier, which
        is why the packet type is also required.

        Used when displaying the reason code.
        """
        ...
    
    def getId(self, name): # -> int:
        """
        Get the numeric id corresponding to a reason code name.

        Used when setting the reason code for a packetType
        check that only valid codes for the packet are set.
        """
        ...
    
    def set(self, name): # -> None:
        ...
    
    def unpack(self, buffer): # -> Literal[1]:
        ...
    
    def getName(self): # -> str:
        """Returns the reason code name corresponding to the numeric value which is set.
        """
        ...
    
    def __eq__(self, other) -> bool:
        ...
    
    def __lt__(self, other) -> bool:
        ...
    
    def __repr__(self): # -> str:
        ...
    
    def __str__(self) -> str:
        ...
    
    def json(self): # -> str:
        ...
    
    def pack(self): # -> bytearray:
        ...
    
    @property
    def is_failure(self) -> bool:
        ...
    


class _CompatibilityIsInstance(type):
    def __instancecheck__(self, other: Any) -> bool:
        ...
    


class ReasonCodes(ReasonCode, metaclass=_CompatibilityIsInstance):
    def __init__(self, *args, **kwargs) -> None:
        ...
    


