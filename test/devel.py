# Import packages
from dataclasses import dataclass, field, fields, is_dataclass
import dataclasses
from operator import is_
import pstats
import socket
import struct
from typing import List

@dataclass(slots = False, frozen = True)
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

# Dictionary: Byte Format Code
BYTE_FORMAT_CODE : dict[type, str] = {
    bool    : COMM_CONST.BOOL,
    bytes   : COMM_CONST.BYTE,
    int     : COMM_CONST.INT,
    float   : COMM_CONST.FLOAT,
    str     : COMM_CONST.STRING,
}

# STRUCT_TYPE : 

# Check if object is iterable
def is_iterable(object) -> bool:
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

# Check if object is a structured-type
def is_struct_type(object) -> bool:
    """
    Check if input-object is a struture type
    :param object: Incomming object
    :return bool: Returns true or false depending on structured-type object or not
    """
    
    # Dataclass
    if is_dataclass(object):
        return True
    # Tuple
    elif type(object) is tuple:
        return True
    # List
    elif type(object) is list:
        return True
    # Set
    elif type(object) is set:
        return True
    # Non-Structured type
    else:
        return False

# Get Byte Format-Code of the incomming data-type
def get_byte_code(indata) -> str:
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
def get_conversion_code(indata) -> str:
    """
    Find the correct complete Conversion-Code of input-data
    Uses the "get_byte_code()"-function to get the correct Format-Code.
    Dependent on the incomming data; If a pure data-type is entered the 
    Conversion-Code will directly correspond to the related Format-Code. 
    If incomming data is iterable, the Conversion-Code is generated based 
    on multiple Format-Codes. 
    :param indata: Incomming Data 
    :return conversion_code: Byte Conversion-Code of in-data
    """

    # Define Byte Conversion-Code variable
    conversion_code = ''

    # Check if in-data is iterable
    if is_iterable(indata):
        # Iterate through incomming data
        for item in indata:
            # Check for additional nested coupling
            # (item of indata is iterable)
            if is_iterable(item):
                # Raise error
                raise TypeError('get_conversion_code: ERROR - To many nested layers of indata')

            # Add Conversion-Code for Item
            conversion_code += get_byte_code(item)

    # In-data is not iterable
    else:
        # Find Conversion-Code for indata
        conversion_code = get_byte_code(indata)

    # Return Conversion-Code
    return conversion_code

@dataclass
class TestClass1():
    name : str = 'olsen'
    age : int = 12
    heigth : float = 1.70

@dataclass
class TestClass2():
    name : str = 'jan'
    age : int = 29
    heigth : float = 1.85
    handsome : bool = False

@dataclass
class TestClass3():
    A : TestClass1
    B : TestClass2

@dataclass()
class TypeMap():
    type : type
    item : object
    item_length : int

@dataclass()
class StructureMap():
    type : type
    length : int
    items : list

# # Get Type-Map Data
# def get_typemap(indata):
#     """
    
#     """
#     # Check if in-data is a structured-type
#     if not is_struct_type(indata):
#         # Raise error
#         raise TypeError('get_structure_data: ERROR - In-Data is NOT a Structured-Type')

#     # Continue
#     else:

#         _type = type(indata)


#         # Special case: In-data is a dataclass
#         if is_dataclass(indata):
#             # Convert dataclass as a tuple 
#             _item = dataclasses.astuple(indata)
#             _type = type(indata).__name__
#             _item_length = len(data)
#         # In-data is a normal structure-type
#         else:
#             data = indata              
#             data_type = type(indata).__name__
#             data_length = len(indata)

#     # Return with data, data-type-name and data-length
#     return (data, data_type, data_length)

# Get Structure-Data
def get_structure(indata):
    """
    Get Struture-Data of input-data
    This includes the data-type-name and data-length
    Note: input-data needs to be a data-structure-type
    If input-data is of dataclass-type, the data is converted to tuple-type
    :param indata: Input Data 
    :return data: Replica of input-data (dataclass is onverted to tuple-type)
    :return data-type: Data-type-name
    :return data-length: Length of Data
    """
    # Check if in-data is a structured-type
    if not is_struct_type(indata):
        # Raise error
        raise TypeError('get_structure_data: ERROR - In-Data is NOT a Structured-Type')

    # Continue
    else:
        # Special case: In-data is a dataclass
        if is_dataclass(indata):
            # Convert dataclass as a tuple 
            data = dataclasses.astuple(indata)
            data_type = type(indata).__name__
            data_length = len(data)
        # In-data is a normal structure-type
        else:
            data = indata              
            data_type = type(indata).__name__
            data_length = len(indata)

    # Return with data, data-type-name and data-length
    return (data, data_type, data_length)

# Get Structure-Map
def get_structure_map_DC(indata):
    
    # Check if in-data is a structured-type
    if is_struct_type(indata):
        
        _data_list = []
        _data = indata
        _data_type = type(indata)
        _data_length = len(indata)

        # # Iterate through the data
        for item in _data:
            if is_struct_type(item):

                _item_list = []
                _item = item
                _item_type = type(item)
                _item_length = len(item)
                
                for elem in item:
                    if is_struct_type(elem):
                        _elem_list = []
                        _elem = elem
                        _elem_type = type(elem)
                        _elem_length = len(elem)

                        for comp in elem:
                            if is_struct_type(comp):
                                # Raise error
                                raise TypeError('get_structure_map: ERROR - Maximum nested layers exceeded')
                            else:
                                _elem_list.append(type(comp))

                        _elem = StructureMap(_elem_type, _elem_length, _elem_list)
                        _item_list.append(_elem)
                    else:
                        _item_list.append(type(elem))
                _item = StructureMap(_item_type, _item_length, _item_list)
                _data_list.append(_item)

            else:
                _data_list.append(type(item))

        data_map = StructureMap(_data_type, _data_length, _data_list)

    # In-data is NOT a structured-type
    else:
        # Raise error
        raise TypeError('get_structure_map: ERROR - In-Data is NOT a Structured-Type')

    return data_map

# Get Structure-Map
def get_structure_map(indata):
    
    # Check if in-data is a structured-type
    if not is_struct_type(indata):
        # Raise error
        raise TypeError('get_structure_map: ERROR - In-Data is NOT a Structured-Type')

    # Continue
    else:
        # Define list of possible items in data
        items = []
        
        # Get Structure-data of in-data
        _data, _data_type, _data_length = get_structure(indata)

        # Iterate through the data
        for item in _data:

            # Items - First layer of nested data in structure
            # ------------------------------
            # Check if item is a structured-type
            if is_struct_type(item):
                # Define list of possible elements in item
                elems = []

                # Get Structure-data of item
                _item, _item_type, _item_length = get_structure(item)

                # Iterate trough item
                for elem in _item:
                    
                    # Elements - Second layer of nested data in structure
                    # ------------------------------
                    # Check if element is a structured-type
                    if is_struct_type(elem):

                        # Define list of possible components in element
                        comps = []

                        # Get Structure-data of item
                        _elem, _elem_type, _elem_length = get_structure(elem)

                        # Iterate trough element
                        for comp in _elem:

                            # Component - Third layer of nested data in structure
                            # ------------------------------
                            # Check if component is a structured-type
                            if is_struct_type(comp):
                                # Raise error
                                raise TypeError('get_structure_map: ERROR - Maximum nested layers exceeded')
                                
                            # Component of item is NOT a structured-type nor iterable
                            else:
                                # Append type-name of item
                                comps.append(type(comp).__name__)

                        # Define and assign Item-Structue-Map   
                        _elem_map = (_elem_type, _elem_length, comps)

                        # Append Item structure
                        elems.append(_elem_map)

                    # Element of item is NOT a structured-type nor iterable
                    else:
                        # Append type-name of item
                        elems.append(type(elem).__name__)

                # Define and assign Item-Structue-Map   
                _item_map = (_item_type, _item_length, elems)

                # Append Item structure
                items.append(_item_map)

            # Item of data is NOT a structured-type nor iterable
            else:
                # Append type-name of item
                items.append(type(item).__name__)

        # Assign Data-Structure-Map values
        data_structure_map = (_data_type, _data_length, items)
        print(data_structure_map)

        # Function return
        return (_data_type, _data_length, items)
        
def restructure(map : StructureMap, indata):

    _data = []
    _type = map.type
    _item_len = map.length
    _items = map.items

    _index = 0
    print('** 1st Layer **')
    for item in _items:

        _item = []
        print('** ITEM **')
        print(item)
        print('\n')
        
        if type(item) is type(map):
            print('** 2nd Layer **')
            print('---------------------')
            _map = item
            
            for sub in _map.items:
                print('** SUB **')
                print(sub)

                print(indata[_index])

                _sub = []
                if type(sub) is type(map):
                    print('** 3rd Layer **')
                    
                    _kart = sub
                    for com in _kart.items:
                        print('** COM **')
                        print(com)
                        print(indata[_index])

                        if com is type(indata[_index]):
                            _sub.append(indata[_index])
                            _index += 1

                    if _kart.type is list:
                        print('is a list')
                        _item.append(_sub)
                    elif _kart.type is tuple:
                        print('is a tuple')
                        _item.append(tuple(_sub))
                    else:
                        print('no type')

                        
                    print('\n')

                elif sub is type(indata[_index]):
                    _item.append(indata[_index])
                    _index += 1

            print('\n')
            print('2nd layer push')
            if _map.type is list:
                print('is a list')
                _data.append(_item)
            elif _map.type is tuple:
                print('is a tuple')
                _data.append(tuple(_item))
            else:
                print('no type')
                # _data = None

            print('\n')

    print('** BUILD TYPE **')
    if _type is list:
        print('is a list')
        data = _data
    elif _type is tuple:
        print('is a tuple')
        data = tuple(_data)
    else:
        print('no type')
        data = None

    return data

def main():

    testClass1 = TestClass1()
    testClass2 = TestClass2()
    testClass3 = TestClass3(testClass1, testClass2)

    print(is_iterable(testClass3))
    print(type(testClass3).__name__)

    A = [11, 22 ,33]
    B = (4.0, 5.0, 6.0)
    C = ('jan', 18, 9.9, False)
    D = [A, B, C, 2]
    E = [A, B, testClass3]
    F = [A, B]


    G = [88, 99]
    H = (3.14, 2.71)
    I  = (G, H)

    J = (F, I)

    K = (J, J)
    I = (A,B)



    data = B
    unpacked_data = tuple(A) + B

    

    print(data)
    print('\n')
    print('---------------------')

    
    map = get_structure_map(data)
    print('\n')
    print('---------------------')

    print(map[0])
    print(map[1])
    print(map[2])
    print('\n')
    print('---------------------')

    print(type(map[0]))
    print(type(map[1]))
    print(type(map[2]))
    print('\n')
    print('---------------------')

    print(unpacked_data)
    print('\n')
    print('---------------------')

    # restructure(map, unpacked_data)
    # print('\n')
    # print('---------------------')
    
def debug():

    A = [11, 22 ,33]
    B = (4.0, 5.0, 6.0)
    C = [A, B]

    D = [88, 99]
    E = (3.14, 2.71)
    F  = (D, E)

    G = (C, F)

    # I = (G, G)
    # J = (A,A)

    data = G

    print(data)
    print('\n')
    print('---------------------')

    map = get_structure_map_DC(data)
    print(map)
    print('\n')
    print('---------------------')

    # print(map.items[0])
    # print(type(map.items[0]))
    # print('\n')
    # print('---------------------')

    indata = tuple(A) + B + tuple(D) + E
    print(indata)
    print('\n')
    print('---------------------')

    unpacked_data = restructure(map, indata)
    print(unpacked_data)
    print('\n')
    print('---------------------')

def test():

    A = (1, 2)

    data_type = type(A)

    B = data_type()

    print(data_type)
    print(type(B))

# Main
# ------------------------------
if __name__ == "__main__":
    
    # main()
    debug()
    # test()