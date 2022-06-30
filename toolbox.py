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
from dataclasses import dataclass, field, fields, is_dataclass, replace
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
    if _iterable(indata):
        # Data is redefined as list
        data = []

        # Loop through incomming data
        for element in indata:
            # Copy element of indata to local variable
            _data = element

            # Get and Update Conversion Code
            conversioncode += get_conversioncode(_data)

            # String: Special case
            if type(_data) is str:
                # String needs to be encoded to byte-value
                _data = _data.encode('UTF-8')

            # Append acquired information to data-array
            data.append(_data)
        
        # Pack data to bytes
        packed_data = struct.pack(_COMM_CONST.Network + conversioncode, *data)
    
    # In-data is not iterable
    else:
        # Get and Update Conversion Code
        conversioncode += get_conversioncode(indata)

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
def unpack_from_bytes(conversioncode : str, packed_data : bytes):
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
            # Assign the Unpacked-Data equals to the only entry of the list
            unpacked_data = _unpacked_data_list[-1]

    # Only one variable to unpack
    else:
        # Assign the Unpacked-data equals to the previously found local variable
        unpacked_data = _unpacked_data

    # Function return
    return unpacked_data

@dataclass
class _CommDataclass():
    """
    Generic Data-Class for communication 
    This Data-Class contains functions related to updating its attributes, 
    finding the Data-Class' Conversion-Code, aswell as packing and unpacking
    the Data-Class to and from bytes (respectively) 
    """

    # Update Dataclass Attributes
    def _update_attributes(self, data_dict : dict):
        """
        Update Dataclass Attributes
        Using data-dictionary (with keys and values) to update the Dataclass attributes
        Usually used together with unpacking from bytes to dataclass 
        :param data_dict: Data-Dictionary in relation to Dataclass attributes
        """
        # Iterate through Data-item
        for key, value in data_dict.items():
            # Check if Dataclass has the attribute 'key'
            if hasattr(self, key):
                # Set Dataclass attribute 'key' equal to value
                setattr(self, key, value)

    # Get Dataclass Conversion-Code
    def get_conversioncode(self) -> str:
        """
        Get Dataclass Conversion-Code
        The Conversion-Code is generated based on the Dataclass attributes, and their respective types.
        This functions used the "Toolbox.get_conversioncode()" to obtain the correct Conversion-Code
        of the input data, using the "Toolbox._COMM_CONST"
        :return conversioncode: Dataclass Conversion-Code (str)
        """
        # Define Conversion-Code
        conversioncode : str = ''

        # Iterate through the fields of the dataclass
        for field in fields(self):
            # Get data for current field
            _name = field.name
            _value = self.__getattribute__(_name)

            # Find and Update Conversion Code
            conversioncode += get_conversioncode(_value)

        # Return Conversion-Code of Dataclass
        return conversioncode

    # Pack Dataclass to Bytes
    def pack_to_bytes(self) -> tuple[bytes, str]:
        """
        Pack the Dataclass to Bytes
        Get data entries from dataclass and pack them to bytes 
        with correct conversion-code for the related data-types
        Packed-data can be used for data-transfer over TCP/UDP
        :return packed_dataclass: Packed Dataclass data (bytes)
        :return conversioncode: Dataclass Conversion-Code (str)
        """
        # Define data to be packed as list
        data : list = []    

        # Iterate through the fields of the dataclass
        for field in fields(self):
            # Get data for current field
            _name = field.name
            _value = self.__getattribute__(_name)

            # Special case: String
            if type(_value) is str:
                # String needs to be encoded to byte-value
                _value = _value.encode('UTF-8')
            
            # Append acquired information to arrays
            data.append(_value)

        # Get Dataclass Conversion-Code
        conversioncode = self.get_conversioncode()

        # Pack Dataclass data to byte
        packed_dataclass = struct.pack(_COMM_CONST.Network + conversioncode, *data)

        # Function return
        return packed_dataclass, conversioncode

    # Unpack Dataclass from Bytes
    def unpack_from_bytes(self, packed_dataclass : bytes, conversioncode : str) -> tuple:
        """
        Unpack the Dataclass from Bytes
        The packed data is converted back to its original Dataclass type(s) using the given conversion-code. 
        This function used the "Toolbox.unpack_from_bytes()" to convert the bytes back to their original type(s) 
        A check on the input conversion-code and the related conversion-code of the dataclass
        is made to ensure incomming data matches the attributes of the dataclass
        Unpacked-data can be used for data-transfer over TCP/UDP
        :param packed_dataclass: Packed data (bytes)
        :param conversionCode: Conversion-Code of packed dataclass (str)
        :return unpacked_dataclass: Packed Dataclass data (bytes)
        :return conversioncode: Dataclass Conversion-Code (str)
        """
        # Define local variables
        _data_dict : dict = {}                  # Data dictionary to update the dataclass
        _index : int = 0                        # Loop-Index
        _conversioncode : str = ''              # Local variable for Input Conversion-Code
        _dataclass_conversioncode : str  = ''   # Local variable for Dataclass Conversion-Code

        # Remove digits from Conversion-Code
        # ------------------------------
        # (Digits are only related to the length of a future string
        # and has no related value in the Packed-Data)
        # Iterate through items of Dataclass Conversion-Code
        for i in conversioncode:
            # Check for non-digits
            if not i.isdigit():
                # Add only non-digit values to local variable for Input Conversion-Code
                _conversioncode += _conversioncode.join(i)

        # Iterate through items of Dataclass Conversion-Code
        for j in self.get_conversioncode():
            # Check for non-digits
            if not j.isdigit():
                # Add only non-digit values to local variable for Dataclass Conversion-Code
                _dataclass_conversioncode += _dataclass_conversioncode.join(j)

        # Compare and ensure that the incomming Conversion-Code matches with the Dataclass Conversion-Code
        if _conversioncode == _dataclass_conversioncode:

            # Unpack data from bytes
            unpacked_dataclass = unpack_from_bytes(conversioncode, packed_dataclass)

            # Iterate through the fields of the dataclass
            for field in fields(self):
                
                # Update Data-dictionary
                # with key from current field-name and value from unpacked data at index
                _data_dict[field.name] = unpacked_dataclass[_index]

                # Update loop-index
                _index += 1

            # Update DataClass with Unpacked data
            self._update_attributes(_data_dict)
            
            # Return Unpacked data
            return unpacked_dataclass

        # Conversion-Codes does NOT match
        else:
            # Report error
            raise ValueError('ERROR: unpack_from_bytes: Incomming Conversion-Code does NOT match dataclass {%s}' %type(dataclass))

@dataclass
class testData(_CommDataclass):
    name : str = 'jan'
    age : int = 29
    heigth : float = 1.85

@dataclass
class testData2(_CommDataclass):
    name : str = 'olsen'
    # age : bool = False
    age : int = 12
    heigth : float = 1.70

    
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
    print(data_test.get_conversioncode())
    print('\n')

    data_test2 = testData2()
    print(data_test2)
    print(data_test2.get_conversioncode())
    print('\n')

    packedData, convCode = data_test.pack_to_bytes()
    print(packedData)
    print(convCode)
    print('\n')

    data_test2.unpack_from_bytes(packedData, convCode)
    print(data_test2)
    print('\n')

    # # kai = testData(name='kai',age=88, heigth=1.92)
    # kai = testData2()
    # print(kai)
    # print('\n')

    # unpackedData = unpack_from_bytes_dataclass(kai, convCode, packedData)
    # print(unpackedData)
    # print(kai)
    # print('\n')

    # kai.update_dict(unpackedData)
    

    # ------------------------------

    # # packedData, convCode = pack_to_bytes_dataclass(data_test)
    # packedData, convCode, datain = pack_to_bytes_dataclass(data_test)
    # print(packedData)
    # print(convCode)
    # print('\n')

    # unpackedData = unpack_from_bytes(convCode, packedData)
    # print(unpackedData)
    # print('\n')

    # data_test.updateWithTuple(unpackedData)
    # print(data_test)


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

    
