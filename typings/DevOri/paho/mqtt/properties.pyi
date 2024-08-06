"""
This type stub file was generated by pyright.
"""

class MQTTException(Exception):
    ...


class MalformedPacket(MQTTException):
    ...


def writeInt16(length): # -> bytearray:
    ...

def readInt16(buf): # -> Any:
    ...

def writeInt32(length): # -> bytearray:
    ...

def readInt32(buf): # -> Any:
    ...

def writeUTF(data): # -> bytearray:
    ...

def readUTF(buffer, maxlen): # -> tuple[Any, Any]:
    ...

def writeBytes(buffer):
    ...

def readBytes(buffer): # -> tuple[Any, Any]:
    ...

class VariableByteIntegers:
    """
    MQTT variable byte integer helper class.  Used
    in several places in MQTT v5.0 properties.

    """
    @staticmethod
    def encode(x): # -> bytes:
        """
          Convert an integer 0 <= x <= 268435455 into multi-byte format.
          Returns the buffer converted from the integer.
        """
        ...
    
    @staticmethod
    def decode(buffer): # -> tuple[Any | Literal[0], int]:
        """
          Get the value of a multi-byte integer from a buffer
          Return the value, and the number of bytes used.

          [MQTT-1.5.5-1] the encoded value MUST use the minimum number of bytes necessary to represent the value
        """
        ...
    


class Properties:
    """MQTT v5.0 properties class.

    See Properties.names for a list of accepted property names along with their numeric values.

    See Properties.properties for the data type of each property.

    Example of use::

        publish_properties = Properties(PacketTypes.PUBLISH)
        publish_properties.UserProperty = ("a", "2")
        publish_properties.UserProperty = ("c", "3")

    First the object is created with packet type as argument, no properties will be present at
    this point. Then properties are added as attributes, the name of which is the string property
    name without the spaces.

    """
    def __init__(self, packetType) -> None:
        ...
    
    def allowsMultiple(self, compressedName): # -> bool:
        ...
    
    def getIdentFromName(self, compressedName): # -> int:
        ...
    
    def __setattr__(self, name, value): # -> None:
        ...
    
    def __str__(self) -> str:
        ...
    
    def json(self): # -> dict[Any, Any]:
        ...
    
    def isEmpty(self): # -> bool:
        ...
    
    def clear(self): # -> None:
        ...
    
    def writeProperty(self, identifier, type, value): # -> bytes:
        ...
    
    def pack(self): # -> bytes:
        ...
    
    def readProperty(self, buffer, type, propslen): # -> tuple[Any | tuple[Any, Any] | Literal[0], int | Any]:
        ...
    
    def getNameFromIdent(self, identifier): # -> str | None:
        ...
    
    def unpack(self, buffer): # -> tuple[Self, Any | int]:
        ...
    


