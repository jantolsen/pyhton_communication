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
from dataclasses import astuple, dataclass, field, is_dataclass
import socket
import struct
import sys

# Dataclass - Communication Constants
@dataclass(frozen = True)
class COMM_CONST:
    """
    Communication Constants
    Data constants for communication configuration
    Includes Address-Family type, Protocol type
    and Byte Code Format
    """

    # Address Family
    IPV4    : int = socket.AF_INET
    IPV6    : int = socket.AF_INET6

    # Communication Protocols
    UDP     : int = socket.SOCK_DGRAM
    TCP     : int = socket.SOCK_STREAM

    # Connection Timeout
    TIMEOUT : float = 1.0 
    
    # Byte Order
    Native          : str = "="  # Native to system OS (sys.byteorder)
    LittleEndian    : str = "<"  # Little-Endian
    BigEndian       : str = ">"  # Big-Endian
    Network         : str = "!"  # Big-Endian

    # Byte Code Conversion Format Characters
    BYTE    : str = "c" # Byte (Byte Size)
    CHAR    : str = "c" # Character (Byte Size: 1)
    SCHAR   : str = "b" # Signed Character (Byte Size: 1)
    UCHAR   : str = "B" # Unsigned Character (Byte Size: 1)
    BOOL    : str = "?" # Bool (Byte Size: 1)
    INT     : str = "h" # Short (Integer) (Byte Size: 2)
    UINT    : str = "H" # Unsigned Short (Integer) (Byte Size: 2)
    DINT    : str = "i" # Double Integer (Byte Size: 4)
    UDINT   : str = "I" # Unsigned Double Integer (Byte Size: 4)
    LINT    : str = "l" # Long Integer (Byte Size: 4)
    ULINT   : str = "L" # Unsigned Long Integer (Byte Size: 4)
    FLOAT   : str = "f" # Float (Real) (Byte Size: 4)
    DOUBLE  : str = "d" # Double (LReal) (Byte Size: 8)
    STRING  : str = "s" # String (char[]) (Byte Size: Char*X)

    # Server and Client IDs
    SERVER          : int = 1
    GUI_CLIENT      : int = 2
    MATLAB_CLIENT   : int = 3


# Dictionary: Byte Format Code
# ------------------------------
BYTE_FORMAT_CODE : dict[type, str] = {
    bool    : COMM_CONST.BOOL,
    bytes   : COMM_CONST.BYTE,
    int     : COMM_CONST.INT,
    float   : COMM_CONST.FLOAT,
    str     : COMM_CONST.STRING,
}

# Dataclass - Communication Header
@dataclass()
class COMM_HEADER():
    """
    Communication Header
    Dataclass is acting as Communication Header for incomming and outgoing data. 
    This contains information such as:
     - Type ID (int) : (Server, GUI, Matlab, etc)
     - Content length (int) : Length of the message's data-content
     - Header length (int) : Length of the message header (default: 32)
     - Encoding (str) : Encoding used by the content (default: utf-8)
     - Byteorder (str) : Byte order of the machine (little-, big-endian) (default: sys.byteorder)    
    """

    type_id : int
    content_length : int
    header_length  : int = field(repr = False, default = 32)
    encoding    : str = field(repr = False, default = 'utf-8')
    byteorder   : str = field(repr = False, default = sys.byteorder)


# Dataclass - Communication Type-Map
@dataclass()
class TypeMap():
    """
    Type-Map Dataclass
    Dataclass for mapping the Type-Structure of a specified data-type
    (dataclass, tuple, list, etc.)
    This includes: object-data, type, item-list and object-size  
    Type-Map is used in remapping of packed data back to original type-structure
    """
    data    : object = None
    type    : type = object
    items   : list = field(default_factory=list)
    size    : int = 0


# Dataclass - Communication Configuration
@dataclass()
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
@dataclass()
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
@dataclass()
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
# ------------------------------
def is_iterable(object) -> bool:
    """
    Check if Input-Object is iterable
    (note String is not considered as iterable type)
    :param object: Input-object
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


# Get Byte Format-Code of the incomming data-type
# ------------------------------
def get_byte_format(indata) -> str:
    """
    Find the corresponding Byte Format-Code of input data-type
    Using the BYTE_FORMAT_CODE dictionary (based on the COMM_CONST dataclass. 
    Note: Input data needs to be a pure data-type
    :param indata: Incomming data (bool, int, float, str) 
    :return format_code: Byte Format-Code of in-data datatype (str)
    """

    # Check for unsupported data-type
    if (type(indata) not in BYTE_FORMAT_CODE):
        raise KeyError('get_format_code: ERROR - Unsupported type {%s}' %type(indata))

    # Get Byte Format-Code of in-data
    else:
        # Use the Byte-Format-Code dictionary to find the correspoding format character
        format_code = BYTE_FORMAT_CODE[type(indata)]
        
        # Special Case: String
        if type(indata) is str:
            # String is handled as an array of chars
            # String-length (number of chars) needs to added to the format character
            string_len = len(indata)                # Find string-length
            no_chars = format(string_len)           # Format string-length number as string
            format_code = no_chars + format_code    # Add string-length number to Byte-Format-Code

    # Return Byte-Format
    return format_code


# Get Byte Conversion Code of input-data
# ------------------------------
def get_byte_conversion(indata) -> str:
    """
    Find the correct complete Conversion-Code of input-data
    Uses the "get_byte_format"-function to get the correct Format-Code.
    Dependent on the incomming data; If a pure data-type is entered the 
    Conversion-Code will directly correspond to the related Format-Code. 
    If incomming data is iterable, the Conversion-Code is generated based 
    on multiple Format-Codes. 
    :param indata: Incomming Data 
    :return conversion_code: Byte Conversion-Code of in-data (str)
    """

    # Define Byte Conversion-Code variable
    conversion_code = ''

    # In-data is Iterable-Type 
    # ------------------------------
    # (list, tuple, etc.)
    if is_iterable(indata):
        # Iterate through incomming data
        for item in indata:
            # Get Item's Byte-Conversion-Code
            _item_conversion_code = get_byte_conversion(item)

            # Add Conversion-Code for Item
            conversion_code += _item_conversion_code
            
    # In-data is Primitive Type
    # ------------------------------ 
    # (int, float, string, etc.)
    else:
        # Generate Byte-Conversion-Code for indata
        conversion_code = get_byte_format(indata)

    # Return Conversion-Code
    return conversion_code


# Pack Data to Bytes
# ------------------------------
def pack_to_bytes(indata) -> tuple[bytes, str, object]:
    """
    Pack data to byte
    Pack incomming data to bytes with correct conversion-code 
    for the related data-types
    Packed-data can be used for data-transfer over TCP/UDP
    :param indata: Data to be packed to bytes
    :return packed_data: Packed data (bytes)
    :return conversion_code: Conversion-Code of packed data (str)
    :return data: Flat-structured copy of indata
    """

    # Define local variables
    conversion_code = '' 
    packed_data = b''
    data = 0

    # In-data is Iterable-Type 
    # ------------------------------
    # (list, tuple, etc.)
    if is_iterable(indata):
        # Data is redefined as list
        data = []

        # Iterate through incomming data
        for item in indata:

            # Item is Iterable-Type 
            # ------------------------------
            # (list, tuple, etc.)
            if is_iterable(item):

                # Pack Item to Bytes
                item_packed_data, item_conversion_code, item_data = pack_to_bytes(item)
                
                # Get and update Conversion Code
                conversion_code += item_conversion_code

                # Item-Data is Iterable-Type 
                # ------------------------------
                # (list, tuple, etc.)
                if is_iterable(item_data):

                    # Iterate through elements of item_data
                    for elem in item_data:
                        # Append element to data-list 
                        data.append(elem)

                # Item-Data is Primitive Type
                # ------------------------------ 
                else:
                    # Append item-data to data-list 
                    data.append(item_data)

            # In-data is Primitive Type
            # ------------------------------ 
            # (int, float, string, etc.)
            else:
                # Get and update Conversion Code
                conversion_code += get_byte_conversion(item)

                # Special case: String
                if type(item) is str:
                    # String needs to be encoded to byte-value
                    item = item.encode('UTF-8')

                # Append item-data to data-list 
                data.append(item)

        # Pack data to bytes
        packed_data = struct.pack(COMM_CONST.Network + conversion_code, *data)

    # In-data is Primitive Type
    # ------------------------------ 
    # (int, float, string, etc.)
    else:
        # Get In-data Conversion Code
        conversion_code = get_byte_conversion(indata)

        # Special case: String
        if type(indata) is str:
            # String needs to be encoded to byte-value
            data = indata.encode('UTF-8')
        # In-data is not string
        else:
            # Assign data equal to indata
            data = indata

        # Pack data to bytes
        packed_data = struct.pack(COMM_CONST.Network + conversion_code, data)

    # Function return 
    return packed_data, conversion_code, data


# Unpack Data from Bytes
# ------------------------------
def unpack_from_bytes(packed_data : bytes, conversion_code : str):
    """
    Unpack data from bytes
    The packed data is converted back to its original type(s)
    using the given conversion-code
    Unpacked-data can be used for data-received over TCP/UDP
    :param packed_data: Packed data (bytes)
    :param conversion_code: Conversion-Code of packed data (str)
    :return data: Unpacked Data
    """
    # Define local variables
    _unpacked_data = b''
    _value = ''
    _index = 0

    # Unpack data from bytes to a local variable
    _unpacked_data = struct.unpack(COMM_CONST.Network + conversion_code, packed_data)

    # Packed Data contains multiple entries
    # ------------------------------ 
    # (multiple variables to unpack)
    if len(conversion_code) > 1:

        # Define Unpacked-Data as list
        _unpacked_data_list = []

        # Iterate through Conversion-Code
        for code in conversion_code:
    
            # Special case: Digit
            if code.isdigit():
                # Digits are only related to the length of a future string
                # and has no related value in the Packed-Data

                # Skip this iteration
                continue

            # Special case: String
            elif code == COMM_CONST.STRING:
                # String needs to be decoded from byte-value
                _value = _unpacked_data[_index].decode('UTF-8')

            # Assign the local value-variable equal to the indexed element of unpacked-data
            else:
                _value = _unpacked_data[_index]

            # Update the index number
            _index += 1

            # Append index value to Unpacked-Data list
            _unpacked_data_list.append(_value)
        
        # Unpacked Data contains multiple entries
        # ------------------------------ 
        if len(_unpacked_data_list) > 1:

            # Unpacked-Data-List contains more than one entry
            # Convert Unpacked-Data-List to a tuple
            unpacked_data = tuple(_unpacked_data_list)

        # Unpacked Data List contains single entry
        # ------------------------------ 
        else:
            # Assign the Unpacked-Data equal to the only entry of the list
            unpacked_data = _unpacked_data_list[-1]
    
    # Packed Data contains single entry
    # ------------------------------ 
    # (Only one variable to unpack)
    else:
        # Assign the Unpacked-data equals to the previously found local variable
        unpacked_data = _unpacked_data[-1]

    # Function return
    return unpacked_data


# Get Type-Map
# ------------------------------
def get_typemap(indata) -> TypeMap:
    """
    Create Type-Map of a Primitive (int, float, string, etc.) 
    or Iterable-Type (list, tuple, etc.)
    Typically used for creating a type-map before packing and unpacking data 
    :param indata : Input data
    :return type_map : TypeMap-class of input-data type-structure
    """

    # Check if in-data is a dataclass
    if is_dataclass(indata):
        # Raise error
        raise TypeError('CommToolbox.get_typemap: ERROR - In-Data is Dataclass, cannot create a type-map')

    # Continue creating a Type-Map of input iterable
    else:

        # Define and assign values to local variables based self-dataclass object
        _data = indata
        _type = type(_data)
        _items = []
        _size = 0 #len(_data) if is_iterable(_data) else 1

        # In-data is Iterable-Type 
        # ------------------------------
        # (list, tuple, etc.) 
        if is_iterable(indata):
            
            # Iterate through the fields of the in-data
            for field in _data:
                
                # Get the data of current field
                _field_data = field
                _field_type = type(_field_data)
                _field_length = len(_field_data) if is_iterable(_field_data) else 1

                # Field-data is Iterable-Type 
                # ------------------------------
                # (list, tuple, etc.) 
                if is_iterable(field):

                    # Get Type-Map of current field to _data
                    _field_map = get_typemap(field)

                    # Create a data-tuple on current field 
                    _item_tuple = (_field_map, _field_length)

                     # Append item-tuple of current field to item-list
                    _items.append(_item_tuple)

                    # Update Size
                    _size += _field_map.size

                # Field-data is Primitive Type
                # ------------------------------ 
                # (int, float, string, etc.)
                else:
                    # Create a data-tuple on current field 
                    _item_tuple = (_field_type, _field_length)

                    # Append item-tuple of current field to item-list
                    _items.append(_item_tuple)

                    # Update Size
                    _size += _field_length
                
        # Creat a Type-Map object of obtained data
        type_map = TypeMap(_data, _type, _items, _size)

        # Function return
        return type_map


# Remap
# ------------------------------
def remap(indata, type_map : TypeMap):
    """
    Re-map In-data to its original type-strucute
    Generate data from flat-structured indata back to its original format
    using the type-structure from the related Type-Map 
    Typically used for creating data with type-map after unpacking data 
    :param indata : Input data (flat data-structure) 
    :param type_map : TypeMap-class of input-data type-structure
    :return data : Re-mapped data
    """

    # Define and assign values to local variables based on Type-Map
    _data_list = []
    _remapped_data = type_map.type 
    _size = type_map.size
    _index = 0  # Loop-index
    
    # Iterate through Map-Items
    # (Map-Items is defined as a list)
    for item in type_map.items:

        _item_type = item[0]    # First entry equals the Type
        _item_len = item[1]     # Second entry equals the length of the Type
        _item_list = []         # Define a Item-list

         # Item is a Type-Map
        # ------------------------------
        # (Nested dataclasses)
        if type(_item_type) is TypeMap:

            # Assign Sub-Values from Item Type-Map
            _sub_typemap = _item_type
            _sub_data = _sub_typemap.data
            _sub_type = _sub_typemap.type
            _sub_items = _sub_typemap.items
            _sub_items_size = _sub_typemap.size
            _sub_indata = []
            
            # Calculate Sub-Indata
            # ------------------------------
            # Original Indata is related to the base TypeMap
            # a Sub-Indata needs to be calculated to match the Sub-TypeMap
            for i in range(_index, _index + _sub_items_size):
                _sub_indata.append(indata[i])

            # Call remap for Sub-Data
            _sub_data = remap(_sub_indata, _sub_typemap)

            # Update loop-index
            _index += _sub_items_size

            # Append Sub-Data to data-list
            _data_list.append(_sub_data)

        # Item is Iterable-Type 
        # ------------------------------ 
        # (list, tuple, etc.)
        elif (_item_type is tuple) or (_item_type is list):
            # Iterate through the length of the Item
            for i in range(_item_len):
                # Append in-data at index to item-list
                _item_list.append(indata[_index])

                # Update loop-index
                _index += 1
            
            # Append item-list to data-list
            _data_list.append(_item_list)

        # Item is a Primitive-Type 
        # ------------------------------ 
        # (int, float, string, etc.)
        else:
            # Ensure indata-type matches
            if type(indata[_index]) != _item_type:
                # Raise error
                raise TypeError('remap: ERROR - In-Data type does NOT match Item-Type')

            # Append in-data at index to data-list
            _data_list.append(indata[_index])

            # Increase loop-index
            _index += 1
    
    # Convert and Update Remapped Data
    # ------------------------------
    # Primitive-Type 
    if not is_iterable(type_map.data):
        # Assign Remapped-Data as Primitive
        _remapped_data = type_map.data

    # Tuple-Type 
    elif type_map.type is tuple:
        # Convert Data-List to tuple
        _data_tuple = tuple(_data_list)

        # Assign Remapped-Data as Tuple
        _remapped_data = _data_tuple

    # List-Type
    elif type_map.type is list:

         # Assign Remapped-Data as List
        _remapped_data = _data_list
    
    # Unsupported type
    else:
        # Raise error
        raise TypeError('remap: ERROR - Type-Map type is unsupported')

    # Function return
    return _remapped_data


# Remap from Bytes
# ------------------------------
def remap_from_bytes(packed_data : bytes, type_map : TypeMap, conversion_code : str):
    """
    Remap from Bytes
    Packed-data (bytes) is used together with the conversion-code 
    and the related Type-Map to generate data with its original type-structure
    :param packed_data : Packed Data (bytes)
    :param type_map : Type-Map of data object to be re-mapped 
    :param conversion_code : Byte-Conversion-Code (str)
    :return data : Re-mapped Object 
    """

    # Unpack Dataclass from bytes
    # (this will create "flat-structured"-data of the data)
    unpacked_data = unpack_from_bytes(packed_data, conversion_code)

    # Remap Data using the Unpacked data (flat-structured)
    remapped_data = remap(unpacked_data, type_map)

    # Function return
    return remapped_data