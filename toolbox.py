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
def checkIterable(object) -> bool:
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

# Find Byte Conversion Code of input
def findConversionCode(indata) -> str:
    """
    Find the correct Conversion-Code of input-data
    Using the _COMM_CONT dataclass
    :param indata: Incomming Data 
    :return conversionCode: Conversion-Code of data
    """
    # Define Conversion-Code variable
    conversioncode = ''

    # Based on data-type assign correct Byte Conversion Code
    # ------------------------------
    # Bool
    if type(indata) is bool:
        conversioncode = _COMM_CONST.BOOL

    # Int
    elif type(indata) is int:
        conversioncode = _COMM_CONST.INT16

    # Float
    elif type(indata) is float:
        conversioncode = _COMM_CONST.FLOAT

    # String
    elif type(indata) is str:
        # String is handled as an array of chars
        string_len = len(indata)                    # Find string-length
        chars = format(string_len)                  # Format string-length number as string
        conversioncode = chars + _COMM_CONST.STR    # Add string-length number to conversion-code constant

    # Unsupported type
    else:
        # Report error
        raise TypeError('ERROR: findConversionCode: Unsupported type {%s}' %type(indata))

    # Return Conversion-Code
    return conversioncode

# Pack Data to Bytes
def packToBytes(indata) -> tuple[bytes, str]:
    """
    Pack data to byte
    Get data from input data and pack them to bytes 
    with correct conversion-code for the related data-types
    Packed-data can be used for data-transfer over TCP/UDP
    :param indata: Data to be packed to bytes
    :return dataPacked: Packed data (bytes)
    :return conversionCode: Conversion-Code of packed data (str)
    """

    # Initialize Function outputs
    conversionCode = '' 
    dataPacked = b''
    data = 0

    # Check if in-data is iterable
    if checkIterable(indata):
        # Data is redefined as list
        data = []

        # Loop through incomming data
        for element in indata:
            # Copy element of indata to local variable
            _data = element

            # Get and Update Conversion Code
            conversionCode += findConversionCode(_data)

            # String: Special case
            if type(_data) is str:
                # String needs to be encoded to byte-value
                _data = _data.encode('UTF-8')

            # Append acquired information to data-array
            data.append(_data)
        
        # Pack data to bytes
        dataPacked = struct.pack(_COMM_CONST.Network + conversionCode, *data)
    
    # In-data is not iterable
    else:
        # Get and Update Conversion Code
        conversionCode += findConversionCode(indata)

        # Special case: String
        if type(indata) is str:
            # String needs to be encoded to byte-value
            data = indata.encode('UTF-8')

        # In-data is not string
        else:
            # Assign data equal to indata
            data = indata

        # Pack data to bytes
        dataPacked = struct.pack(_COMM_CONST.Network + conversionCode, data)

    # Function return 
    return dataPacked, conversionCode

# Pack Dataclass to byte
def packToBytes_DataClass(dataclass) -> tuple[ bytes, str, list]:
    """
    Pack DataClass to byte
    Get data entries from dataclass and pack them to bytes 
    with correct conversion-code for the related data-types
    Packed-data can be used for data-transfer over TCP/UDP
    :param dataclass: Dataclass to be packed to bytes
    :return data: Dataclass data (list)
    :return dataPacked: Packed Dataclass data (bytes)
    :return conversionCode: Conversion-Code of packed data (str)
    """

    # Initialize Function outputs
    conversionCode = '' 
    dataPacked = b''
    indata = 0

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

            # Get and Update Conversion Code
            conversionCode += findConversionCode(_value)

            # Special case: String
            if type(_value) is str:
                # String needs to be encoded to byte-value
                _value = _value.encode('UTF-8')

            # Append acquired information to arrays
            field_name.append(_name)
            field_value.append(_value)

        # Dataclass Data
        indata = field_value

        # Pack Dataclass data to byte
        dataPacked = struct.pack(_COMM_CONST.Network + conversionCode, *indata)
    
    # Incomming data is NOT dataclass
    else:
        # Report error
        raise TypeError('ERROR: pack2byte_DataClass: Incomming data is NOT dataclass {%s}' %type(dataclass))

    # Function return 
    return dataPacked, conversionCode, indata

# Unpack Data from Bytes
def unpackFromBytes(conversionCode : str, packedData : bytes):
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
    _unpackedData = b''
    _value = ''
    _index = 0

    # Unpack data from bytes to a local variable
    _unpackedData = struct.unpack(_COMM_CONST.Network + conversionCode, packedData)

    # Determine if Packed-Data contains more than one-variable
    if len(conversionCode) > 1:

        # Define Unpacked-Data as list
        unpackedDataList = []
        
        # Iterate through Conversion-Code
        for code in conversionCode:
            
            # Special case: Digit
            if code.isdigit():
                # If a digit is present in the Conversion-Code
                # its related to the length of a future string
                # and has no related value in the Packed-Data

                # Skip this iteration
                continue

            # Special case: String
            elif code == _COMM_CONST.STR:
                # String needs to be decoded from byte-value
                _value = _unpackedData[_index].decode('UTF-8')

            # Assign the local value-variable equal to the indexed element of unpackedData
            else:
                _value = _unpackedData[_index]

            # Update the index number
            _index += 1

            # Append index value to Unpacked-Data list
            unpackedDataList.append(_value)

        # Check length of list
        if len(unpackedDataList) > 1:

            # Unpacked-Data-List contains more than one entry
            # Convert Unpacked-Data-List to a tuple
            unpackedData = tuple(unpackedDataList)

        # List length is only one entry
        else:
            # Assign the Unpacked-Data equals to the only entry of the list
            unpackedData = unpackedDataList[-1]

    # Only one variable to unpack
    else:
        # Assign the Unpacked-data equals to the previously found local variable
        unpackedData = _unpackedData

    # Function return
    return unpackedData

# Unpack Data from Bytes
def unpackFromBytes_DataClass(conversionCode : str, packedData : bytes) -> tuple:
    """
    Unpack Data-class from bytes 
    The packed data is converted back to its original dataclass type(s)
    using the given conversion-code
    Unpacked-data can be used for data-received over TCP/UDP
    :param dataPacked: Packed data (bytes)
    :param conversionCode: Conversion-Code of packed data (str)
    :return data: Unpacked Data (tuple)
    """
    raise NotImplementedError()


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
    def update(self, name : str, age : int, height : float):
        self.name = name
        self.age = age
        self.heigth = height

    def updateWithTuple(self, data : tuple):
        
        self.update(data[0], data[1], data[2])

# Main Function
# ------------------------------
if __name__ == "__main__":
    communicationConstants = _COMM_CONST()

    # TEST & DEBUG
    # ------------------------------


    # data_test = ('hei jan', 'hei birger', 88.99, True)
    # print(data_test)
    # print('\n')
    
    data_test = testData()
    print(data_test)


    # packedData, convCode = packToBytes(data_test)
    packedData, convCode, datain = packToBytes_DataClass(data_test)
    print(packedData)
    print(convCode)
    print('\n')

    unpackedData = unpackFromBytes(convCode, packedData)
    print(unpackedData)
    print('\n')

    data_test.updateWithTuple(unpackedData)
    print(data_test)


    # # kai = testData(name='kai',age=88, heigth=1.92)
    # # jan = testData()
    # # print(jan)
    # # print('\n')

    # # data_test = 'Geir', 52, 1.71
    # # print(data_test)
    # # print(type(data_test))

    # # print(checkIterable(data_test))
    # # print('\n')
    

    # # data, data_packed, conv_code = packToBytes(data_test)
    # # print(conv_code)
    # # print(data)
    # # print(data_packed)
    # # print('\n')

    # # unpacked = struct.unpack(_COMM_CONST.Network + conv_code, data_packed)
    # # print(unpacked)
    # # print(type(unpacked))
    # # print(unpacked[1])
    # # print('\n')

    # # # jan.update(unpacked[0].decode('UTF-8'), unpacked[1], unpacked[2])
    # # jan.updateWithTuple(unpacked)
    # # print(jan)

    
