# Communication Toolbox
# ------------------------------
# Description:
# Toolbox for utility classes and methods
# to be used with a communication connection

# Version
# ------------------------------
# 0.0   -   Initial version
#           [26.06.2022] - Jan T. Olsen

# Import packages
from dataclasses import dataclass, field, fields, is_dataclass
import socket
import struct

# Dataclass - Communication Constants
@dataclass(slots=False)
class _COMM_CONST:
    """
    Communication Constants
    Data constants for communication configuration
    Includes Address-Family type and Protocol type
    """

    # Address Family
    IPV4    : int = socket.AF_INET
    IPV6    : int = socket.AF_INET6

    # Communication Protocols
    UDP     : int = socket.SOCK_DGRAM
    TCP     : int = socket.SOCK_STREAM

    # Byte Order
    Native          : str = "="  # Native to system OS (sys.byteorder)
    LittleEndian    : str = "<"  # Little-Endian
    BigEndian       : str = ">"  # Big-Endian
    Network         : str = "!"  # Big-Endian

    # Format Characters
    CHAR            : str = "c"  # Character (Byte Size: 1)
    SCHAR           : str = "b"  # Signed Character (Byte Size: 1)
    UCHAR           : str = "B"  # Unsigned Character (Byte Size: 1)
    BOOL            : str = "?"  # Bool (Byte Size: 1)
    INT16           : str = "h"  # Short (Integer) (Byte Size: 2)
    UINT16          : str = "H"  # Unsigned Short (Integer) (Byte Size: 2)
    DINT            : str = "i"  # Double Integer (Byte Size: 4)
    UDINT           : str = "I"  # Unsigned Double Integer (Byte Size: 4)
    LINT            : str = "l"  # Long Integer (Byte Size: 4)
    ULINT           : str = "L"  # Unsigned Long Integer (Byte Size: 4)
    FLOAT           : str = "f"  # Float (Real) (Byte Size: 4)
    DOUBLE          : str = "d"  # Double (LReal) (Byte Size: 8)
    STR             : str = "s"  # String (char[]) (Byte Size: Char*X)

# Dataclass - Communication Configuration
@dataclass(slots=False)
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
@dataclass(slots=False)
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
@dataclass(slots=False)
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

# Check if object is iterable
def _iterable(object) -> bool:
    """
    Check if input-object is iterable
    (note String is not considered as iterable type)
    :param object: Incomming object
    :return bool: Returns true or false depending on iterable object or not
    """
    # Try to get an iterator from the object
    try:
        it = iter(object)

        # Check if object is String
        if type(object) is str:
            return False
        # Object is iterable
        else:
            return True
    # Failed to get an iterator from object
    except TypeError: 
        # Return non-iterable status
        return False

# Find Byte Conversion Code based on data-type
def find_conversioncode(data) -> str:
    """
    Find the corresponding Conversion-Code of input data
    Using the _COMM_CONT dataclass. Note: input data needs to be a pure data-type
    :param datatype: Incomming Datatype (bool, int, float, str) 
    :return conversionCode: Conversion-Code of datatype (str)
    """
    # Bool
    if type(data) is bool:
        conversioncode = _COMM_CONST.BOOL

    # Int
    elif type(data) is int:
        conversioncode = _COMM_CONST.INT16

    # Float
    elif type(data) is float:
        conversioncode = _COMM_CONST.FLOAT

    # String
    elif type(data) is str:
        # String is handled as an array of chars
        string_len = len(data)                    # Find string-length
        chars = format(string_len)                  # Format string-length number as string
        conversioncode = chars + _COMM_CONST.STR    # Add string-length number to conversion-code constant

    # Iterable
    elif _iterable(data):
        # Report error
        raise TypeError('ERROR: findConversionCode: Iterable type is not supported {%s}' %type(data))

    # Unsupported type
    else:
        # Report error
        raise TypeError('ERROR: findConversionCode: Unsupported type {%s}' %type(data))

    # Return Conversion-Code
    return conversioncode

# Get Byte Conversion Code of input-data
def get_conversioncode(indata) -> str:
    """
    Find the correct Conversion-Code of input-data
    Using the _COMM_CONT dataclass
    :param indata: Incomming Data 
    :return conversionCode: Conversion-Code of data
    """
    # Define Conversion-Code variable
    conversioncode = ''

    # Check if in-data is iterable
    if _iterable(indata):

        # Iterate through incomming data
        for item in indata:

            # Check for additional nested coupling
            # (item of indata is iterable)
            if _iterable(item):
                # Raise error
                raise TypeError('ERROR: get_conversioncode: To many nested layers of indata')

            # Add Conversion-Code for Item
            conversioncode += find_conversioncode(item)

    # In-data is not iterable
    else:
        # Find Conversion-Code for indata
        conversioncode += find_conversioncode(indata)

    # Return Conversion-Code
    return conversioncode

# Pack Data to Bytes
def pack_to_bytes(indata) -> tuple[bytes, str]:
    """
    Pack data to byte
    Get data from input data and pack them to bytes 
    with correct conversion-code for the related data-types
    Packed-data can be used for data-transfer over TCP/UDP
    :param indata: Data to be packed to bytes
    :return packed_data: Packed data (bytes)
    :return conversionCode: Conversion-Code of packed data (str)
    """
    # Initialize Function outputs
    conversioncode = '' 
    packed_data = b''
    data = 0

    # Check if in-data is iterable
    # (Ex.: Tuple, List, Set)
    if _iterable(indata):
        # Data is redefined as list
        data = []

        # Iterate through incomming data
        for item in indata:
            # Check if item of in-data is iterable
            # (in-data contains nested iterable types)
            # Ex.: tuple(s) within a tuple
            if _iterable(item):
                # Iterate through item
                for element in item:
                    # Check for additional nested coupling
                    # (element of item of indata is iterable)
                    if _iterable(element):
                        # Raise error
                        raise TypeError('ERROR: pack_to_bytes: To many nested layers of In-data')

                    # Get and Update Conversion Code
                    conversioncode += get_conversioncode(element)

                    # String: Special case
                    if type(element) is str:
                        # String needs to be encoded to byte-value
                        element = element.encode('UTF-8')

                    # Append acquired information to data-array
                    data.append(element)

            # Item is not iterable
            else:
                # Get and Update Conversion Code
                conversioncode += get_conversioncode(item)

                # String: Special case
                if type(item) is str:
                    # String needs to be encoded to byte-value
                    item = item.encode('UTF-8')

                # Append acquired information to data-array
                data.append(item)
        
        # Pack data to bytes
        packed_data = struct.pack(_COMM_CONST.Network + conversioncode, *data)
    
    # In-data is not iterable
    else:
        # Get and Update Conversion Code
        conversioncode = get_conversioncode(indata)

        # Special case: String
        if type(indata) is str:
            # String needs to be encoded to byte-value
            data = indata.encode('UTF-8')

        # In-data is not string
        else:
            # Assign data equal to indata
            data = indata

        # Pack data to bytes
        packed_data = struct.pack(_COMM_CONST.Network + conversioncode, data)

    # Function return 
    return packed_data, conversioncode

# Unpack Data from Bytes
def unpack_from_bytes(packed_data : bytes, conversioncode : str):
    """
    Unpack data from bytes
    The packed data is converted back to its original type(s)
    using the given conversion-code
    Unpacked-data can be used for data-received over TCP/UDP
    :param dataPacked: Packed data (bytes)
    :param conversionCode: Conversion-Code of packed data (str)
    :return data: Unpacked Data
    """
    # Define local variables
    _unpacked_data = b''
    _value = ''
    _index = 0

    # Unpack data from bytes to a local variable
    _unpacked_data = struct.unpack(_COMM_CONST.Network + conversioncode, packed_data)

    # Determine if Packed-Data contains more than one-variable
    if len(conversioncode) > 1:

        # Define Unpacked-Data as list
        _unpacked_data_list = []
        
        # Iterate through Conversion-Code
        for code in conversioncode:
    
            # Special case: Digit
            if code.isdigit():
                # Digits are only related to the length of a future string
                # and has no related value in the Packed-Data

                # Skip this iteration
                continue

            # Special case: String
            elif code == _COMM_CONST.STR:
                # String needs to be decoded from byte-value
                _value = _unpacked_data[_index].decode('UTF-8')

            # Assign the local value-variable equal to the indexed element of unpackedData
            else:
                _value = _unpacked_data[_index]

            # Update the index number
            _index += 1

            # Append index value to Unpacked-Data list
            _unpacked_data_list.append(_value)

        # Check length of list
        if len(_unpacked_data_list) > 1:

            # Unpacked-Data-List contains more than one entry
            # Convert Unpacked-Data-List to a tuple
            unpacked_data = tuple(_unpacked_data_list)

        # List length is only one entry
        else:
            # Assign the Unpacked-Data equal to the only entry of the list
            unpacked_data = _unpacked_data_list[-1]

    # Only one variable to unpack
    else:
        # Assign the Unpacked-data equals to the previously found local variable
        unpacked_data = _unpacked_data

    # Function return
    return unpacked_data

def convert_to_type(data, type_info):

    if _iterable(type_info):

        for item in type_info:
            raise NotImplementedError



