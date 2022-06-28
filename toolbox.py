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
from dataclasses import dataclass, field, fields, is_dataclass
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

# Pack to Bytes
def packDataToBytes(*data_in):

    
    # Loop through incomming data
    for data in data_in:
        
        # Initialize Conversion-Code
        conversionCode = _COMM_CONST.Network

        # Check if data element is a dataclass
        if is_dataclass(data):
            

            # Declare field variables
            field_name = []
            field_type = []
            field_value = []    

            # Loop through the fields of the dataclass
            for field in fields(data):
                
                # Get information for current field of data
                _name = field.name
                _value = data.__getattribute__(_name)
                _type = type(_value)

                # Append acquired information to arrays
                field_name.append(_name)
                field_value.append(_value)
                field_type.append(_type)

                conversionCode += findConversionCode(_type)

            # Pack dataclass-data to byte
            # byte


            print(field_name)
            print(field_type)
            print(field_value)

        print(conversionCode)

# Pack data-class to byte
def pack2byte_DataClass(dataclass):

    # Initialize Function outputs
    conversionCode = '' 
    dataPacked = ''
    data = 0

    # Declare field variables
    field_name = []
    field_type = []
    field_value = []  

    # Ensure that incomming data is a dataclass
    if is_dataclass(dataclass):

        # Loop through the fields of the dataclass
        for field in fields(dataclass):
            
            # Get information for current field of data
            _name = field.name
            _value = dataclass.__getattribute__(_name)
            _type = type(_value)

            # Update Conversion Code
            conversionCode += findConversionCode(_value)

            # Special case:
            if _type is str:
                # String needs to be encoded to byte-value
                _value = _value.encode('UTF-8')

            # Append acquired information to arrays
            field_name.append(_name)
            field_value.append(_value)
            field_type.append(_type)

        # Dataclass Data
        data = field_value

        # Pack Dataclass data to byte
        dataPacked = struct.pack(_COMM_CONST.Network + conversionCode, *field_value)
    else:
        # Report error
        print('ERROR: pack2byte_DataClass: Incomming data is NOT dataclass {%s}' %type(dataclass))
        pass

    return conversionCode, data, dataPacked

# Find Byte Conversion Code of input
def findConversionCode(data) -> str:

    # Define Conversion-Code variable
    conversioncode = ''

    # Based on data-type assign correct Byte Conversion Code
    # ------------------------------
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
        string_len = len(data)                      # Find string-length
        chars = format(string_len)                  # Format string-length number as string
        conversioncode = chars + _COMM_CONST.STR    # Add string-length number to conversion-code constant
    # Unsupported type
    else:
        # Report error
        print('ERROR: findConversionCode: Unsupported type {%s}' %type(data))
        pass

    # Return Conversion-Code
    return conversioncode

@dataclass
class testData():
    name : str = 'jan'
    age : int = 29
    heigth : float = 1.85

    # _typeConversion : str = ''

    # def __post_init__(self):
    #     # Loop through the fields of the dataclass
    #     for field in fields(self):
    #         _name = field.name
    #         _value = self.__getattribute__(_name)
    #         _type = type(_value)

    #         print(_name)
    #         print(_value)
    #         print(_type)
    #         # _typeConversion

# Main Function
# ------------------------------
if __name__ == "__main__":
    communicationConstants = _COMM_CONST()


    jan = testData()
    kai = testData(name='kai',age=88, heigth=1.92)

    cCode1, data, data_packed = pack2byte_DataClass(jan)
    print(cCode1)
    print(data)
    print(data_packed)
    print('\n')


    code = _COMM_CONST.Network + cCode1 
    unpacked = struct.unpack(code, data_packed)
    print(unpacked)

    bytePacked = struct.pack(code, *data)
    print(data_packed)

    print('\n')

    unpacked = struct.unpack(code, bytePacked)
    print(unpacked)

    name = unpacked[0].decode('UTF-8')
    age = unpacked[1]
    height = unpacked[2]
    print(name)
    print(age)
    print(height)

    
