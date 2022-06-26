# Communication Toolbox
# ------------------------------
# Description:
# Toolbox for utility classes and methods
# to be used with an communication

# Version
# ------------------------------
# 0.0   -   Initial version
#           [26.06.2022] - Jan T. Olsen

# Import packages
from ctypes import sizeof
from dataclasses import dataclass, field
from http.client import NETWORK_AUTHENTICATION_REQUIRED
import socket
import struct

# Dataclass - Communication Constants
@dataclass
class _COMM_CONST:
    """
    Communication Constants
    Data constants for communication configuration
    Includes Address-Family type and Protocol type
    """

    # Address Family
    _IPV4   : int = socket.AF_INET
    _IPV6   : int = socket.AF_INET6

    # Communication Protocols
    _UDP    : int = socket.SOCK_DGRAM
    _TCP    : int = socket.SOCK_STREAM

    # Byte Order
    _Native         : str = "="  # Native to system OS (sys.byteorder)
    _LittleEndian   : str = "<"  # Little-Endian
    _BigEndian      : str = ">"  # Big-Endian
    _Network        : str = "!"  # Big-Endian

    # Format Characters
    _CHAR           : str = "c"  # Character (Byte Size: 1)
    _SCHAR          : str = "b"  # Signed Character (Byte Size: 1)
    _UCHAR          : str = "B"  # Unsigned Character (Byte Size: 1)
    _BOOL           : str = "?"  # Bool (Byte Size: 1)
    _INT16          : str = "h"  # Short (Integer) (Byte Size: 2)
    _UINT16         : str = "H"  # Unsigned Short (Integer) (Byte Size: 2)
    _INT32          : str = "i"  # Integer (Byte Size: 4)
    _UINT32         : str = "I"  # Unsigned Integer (Byte Size: 4)
    _LINT           : str = "l"  # Long Integer (Byte Size: 4)
    _ULINT          : str = "L"  # Unsigned Long Integer (Byte Size: 4)
    _FLOAT          : str = "f"  # Float (Byte Size: 4)
    _STR            : str = "s"  # String (char[]) (Byte Size: Char*X)

# Dataclass - Communication Configuration
@dataclass
class _CommConfig:
    """
    Communication Configuration
    Data container for Communication Configuration parameters
    Includes IP-Address, Port and Buffer-Size
    """

    IP: str = field(init=False)
    Port: int = field(init=False)
    BufferSize: int = field(init=False)
    Config: tuple = field(init=False)

    def __post_init__(self) -> None:
        self.Config = (self.IP, self.Port)


# Dataclass - Communication Configuration
@dataclass
class LocalConfig(_CommConfig):
    """
    Communication Configuration Local
    Inherits the generic Communication Configuration (_COMM_CONFIG)
    Data container for Communication Configuration parameters
    Includes IP-Address, Port and Buffer-Size
    """

    IP: str = field(default="127.0.0.1")
    Port: int = field(default=22000)
    BufferSize: int = field(default=512)
    Config: tuple = field(init=False)

    def __post_init__(self) -> None:
        self.Config = (self.IP, self.Port)


# Dataclass - Communication Configuration
@dataclass
class RemoteConfig(_CommConfig):
    """
    Communication Configuration Remote
    Inherits the generic Communication Configuration (_COMM_CONFIG)
    Data container for Communication Configuration parameters
    Includes IP-Address, Port and Buffer-Size
    """

    IP: str = field(default="127.0.0.1")
    Port: int = field(default=23000)
    BufferSize: int = field(default=512)
    Config: tuple = field(init=False)

    def __post_init__(self) -> None:
        self.Config = (self.IP, self.Port)


# Main Function
# ------------------------------
if __name__ == "__main__":
    communicationConstants = _COMM_CONST()

    print(communicationConstants)
    print(communicationConstants._IPV4)
    print(communicationConstants._UDP)
    print("\n")

    local = LocalConfig(IP="10.0.0.1", Port=22001, BufferSize=1024)
    remote = RemoteConfig()
    print(local)
    print(local.IP)
    print(local.Port)
    print(local.BufferSize)
    print(local.Config)
    print("\n")

    # testing = _COMM_CONFIG()

    def test(config: _CommConfig):

        print(config)
        print(config.IP)
        print(config.Port)
        print(config.BufferSize)
        print(config.Config)
        print("\n")

    test(local)
    test(remote)

    print(type(local.Config))
    print(len(local.Config))
    print(type(local.Config[1]))

    if type(local.Config) is tuple:
        print("YEY")
