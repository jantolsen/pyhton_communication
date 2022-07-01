# Import packages
from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
import struct

@dataclass(slots=False)
class _BYTE_FORMAT:
    # Byte Order
    Native          : str = "="  # Native to system OS (sys.byteorder)
    LittleEndian    : str = "<"  # Little-Endian
    BigEndian       : str = ">"  # Big-Endian
    Network         : str = "!"  # Big-Endian

    # Conversion to Byte Format Characters
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

BYTE_FORMAT : dict[type, str] = {
        bool    : _BYTE_FORMAT.BOOL,
        bytes   : _BYTE_FORMAT.BYTE,
        int     : _BYTE_FORMAT.INT,
        float   : _BYTE_FORMAT.FLOAT,
        str     : _BYTE_FORMAT.STRING,
}

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

# Find Byte Format of the incomming data-type
def get_byte_format(indata) -> str:
    """
    Find the corresponding Byte Format of input data
    Using the BYTE_FORMAT dictionary (based on the _BYTE_FORMAT dataclass. 
    Note: input data needs to be a pure data-type
    :param datatype: Incomming Datatype (bool, int, float, str) 
    :return byteformat: Byte-Format of datatype (str)
    """

    # Check for unsupported data-type
    if (type(indata) not in BYTE_FORMAT):
        raise KeyError('ERROR: get_byte_format_code: Unsupported type {%s}' %type(indata))

    # Get Byte-Format of in-data
    else:
        # Use the Byte-Format dictionary which returns the correspoding format character
        byteformat = BYTE_FORMAT[type(indata)]
        
        # Special Case: String
        if type(indata) is str:
            # String is handled as an array of chars
            # String-length (number of chars) needs to added to the format character
            string_len = len(indata)        # Find string-length
            no_chars = format(string_len)   # Format string-length number as string
            byteformat = no_chars + byteformat  # Add string-length number to Byte-Format

    # Return Byte-Format
    return byteformat

def main():

    # BYTE_FORMAT[bool] = ByteFormatClass.BOOL

    # a = ByteFormat.BOOL

    int_value = 12
    data_type = type(int_value)
    
    print(data_type)

    print(type(data_type))

    print('\n')
    print(BYTE_FORMAT)

    b = []

    val = b
    # val = int_value

    if (type(val) not in BYTE_FORMAT):
        raise KeyError('ERROR: findConversionCode: Unsupported type {%s}' %type(b))
    else:
        print(BYTE_FORMAT[type(val)])


    

    print('\n')
    print('--------------')
    a = 12
    temp = 5
    b = temp.to_bytes(1, 'little')
    print(b)
    c = b'\x03'
    print(int.from_bytes(c, "little"))

    packed = struct.pack('!fc', a, c)
    print(packed)
    print('\n')

    unpacked = struct.unpack('!fc',packed)
    print(unpacked[0], int.from_bytes(unpacked[1],'little'))


# Main
# ------------------------------
if __name__ == "__main__":
    
    main()