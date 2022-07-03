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
    data    : object
    type    : type
    items   : list

@dataclass()
class StructureMap():
    type : type
    length : int
    items : list

# Create Type-Map of Dataclass
def create_typemap_class(indata) -> TypeMap:
    """
    """

    # Check if in-data is a dataclass
    if not is_dataclass(indata):
        # Raise error
        raise TypeError('create_typemap_class: ERROR - In-Data is NOT a Dataclass, cannot create a dataclass type-map')

    # Continue creating a Type-Map of input dataclass
    else:
        # Assign values to local variables based on in-data
        _data = indata
        _type = type(indata)
        _items = []

        # Layer No. 1 - Iteration 
        # ------------------------------
        # Iterate through the fields of the in-data's dataclass
        for field in fields(_data):
            
            # Get the data of current field
            _field_name = field.name
            _field_data = _data.__getattribute__(_field_name)
            _field_type = type(_field_data)
            _field_items = []

            # Layer No. 2 - Data
            # ------------------------------
            # Field-data is a dataclass
            if is_dataclass(_field_data):
                
                # Layer No. 2 - Iteration
                # ------------------------------
                # Iterate through the fields of the field-data's dataclass
                for elem in fields(_field_data):
                    
                    # Get the data of current field
                    _elem_name = elem.name
                    _elem_data = _field_data.__getattribute__(_elem_name)
                    _elem_type = type(_elem_data)
                    # _elem_items = []

                    # Layer No. 3 - Data
                    # ------------------------------
                    # Element-data is a dataclass
                    if is_dataclass(_elem_data):
                        # Raise error
                        raise StopIteration('create_typemap_class: ERROR - Maximum nested layers exceeded')

                    # Element-data is NOT a dataclass
                    else:
                        # Create a data-tuple on current element 
                        _elem_tuple = (_elem_name, _elem_type)

                        # Append data-tuple of current field to item-list
                        _field_items.append(_elem_tuple)
                    # ------------------------------
                    # End - Layer No. 3 - Data
                # ------------------------------
                # End - Layer No. 2 Iteration

                # Generate a Type-Map of current field
                _field_map = TypeMap(_field_data, _field_type, _field_items) 

                # Append data on current field to item-list
                _items.append(_field_map)

            # Field-data is NOT a dataclass
            else:
                # Create a data-tuple on current field 
                _item_tuple = (_field_name, _field_type)

                # Append data-tuple of current field to item-list
                _items.append(_item_tuple)
            # ------------------------------
            # End - Layer No. 2 - Data
        # ------------------------------
        # End - Layer No. 1 Iteration

        # Creat a Type-Map object of obtained data
        type_map = TypeMap(_data, _type, _items)

    # Function return
    return type_map

# Create Type-Map of Iterable
def create_typemap_iter(indata) -> TypeMap:
    """
    """

    # Check if in-data is iterable
    if not is_iterable(indata):
        # Raise error
        raise TypeError('create_typemap_iter: ERROR - In-Data is iterable, cannot create a type-map')

    # Continue creating a Type-Map of input iterable
    else:
        # Assign values to local variables based on in-data
        _data = indata
        _type = type(indata)
        _items = []

        # Layer No. 1 - Iteration 
        # ------------------------------
        # Iterate through the fields of the in-data
        for field in _data:
            
            # Get the data of current field
            _field_data = field
            _field_type = type(_field_data)
            _field_items = []

            # Layer No. 2 - Data
            # ------------------------------
            # Field-data is a iterable
            if is_iterable(_field_data):
                
                # Layer No. 2 - Iteration
                # ------------------------------
                # Iterate through the fields of the field-data's dataclass
                for elem in _field_data:
                    
                    # Get the data of current field
                    _elem_data = elem
                    _elem_type = type(_elem_data)
                    _elem_items = []

                    # Layer No. 3 - Data
                    # ------------------------------
                    # Element-data is a iterable
                    if is_iterable(_elem_data):

                        # Layer No. 3 - Iteration
                        # ------------------------------
                        # Iterate through the fields of the field-data's dataclass
                        for comp in _elem_data:
                            
                            # Get the data of current field
                            _comp_data = comp
                            _comp_type = type(_comp_data)
                            # _comp_items = []

                            # Layer No. 4 - Data
                            # ------------------------------
                            # Component-data is a iterable
                            if is_iterable(_comp_data):
                                # Raise error
                                raise StopIteration('create_typemap_iter: ERROR - Maximum nested layers exceeded')

                            # Component-data is NOT iterable
                            else:
                                # Create a data-tuple on current element 
                                _comp_tuple = (_comp_data, _comp_type)

                                # Append data-tuple of current field to item-list
                                _elem_items.append(_comp_tuple)
                            # ------------------------------
                            # End - Layer No. 4 - Data
                        # ------------------------------
                        # End - Layer No. 3 Iteration

                        # Generate a Type-Map of current field
                        _elem_map = TypeMap(_elem_data, _elem_type, _elem_items) 

                        # Append data on current field to item-list
                        _field_items.append(_elem_map)

                    # Layer No. 3 (Element-data) is NOT iterable
                    else:
                        # Create a data-tuple on current element 
                        _elem_tuple = (_elem_data, _elem_type)

                        # Append data-tuple of current field to item-list
                        _field_items.append(_elem_tuple)
                    # ------------------------------
                    # End - Layer No. 3 - Data
                # ------------------------------
                # End - Layer No. 2 Iteration

                # Generate a Type-Map of current field
                _field_map = TypeMap(_field_data, _field_type, _field_items) 

                # Append data on current field to item-list
                _items.append(_field_map)

            # Layer No. 2 (Field-data) is NOT iterable
            else:
                # Create a data-tuple on current field 
                _item_tuple = (_field_data, _field_type)

                # Append data-tuple of current field to item-list
                _items.append(_item_tuple)
            # ------------------------------
            # End - Layer No. 2 - Data
        # ------------------------------
        # End - Layer No. 1 Iteration

        # Creat a Type-Map object of obtained data
        type_map = TypeMap(_data, _type, _items)

    # Function return
    return type_map

# Get Type-Map Data
def get_typemap(indata) -> TypeMap:
    """
    """

    # Check if in-data is a structured-type
    if not is_struct_type(indata):
        # Raise error
        raise TypeError('get_typemap: ERROR - In-Data is NOT a Structured-Type, cannot create a type-map')

    # Continue
    else:

        # In-data is a dataclass-type
        if is_dataclass(indata):
            
            # Create a Dataclass Type-Map of in-data 
            type_map = create_typemap_class(indata)

        # In-data is iterable
        # (type: list, tuple, set, etc.)
        elif is_iterable(indata):
            
            # Create a Dataclass Type-Map of in-data 
            type_map = create_typemap_iter(indata)

        # Error
        else:
            # Raise error
            raise TypeError('get_typemap: ERROR - In-Data is Unknown Structured-Type, cannot create a type-map')

    # Function return
    return type_map

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
        _data_length = 0 #len(indata)

        # Iterate through the data
        for item in _data:
            if is_struct_type(item):

                _item_list = []
                _item = item
                _item_type = type(item)
                _item_length = 0 #len(item)
                
                for elem in item:
                    if is_struct_type(elem):
                        _elem_list = []
                        _elem = elem
                        _elem_type = type(elem)
                        _elem_length = 0 #len(elem)

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

    testClass1_tuple = dataclasses.astuple(testClass1)
    testClass3_tuple = dataclasses.astuple(testClass3)
    

    print(' CLASS no. 1')
    print('---------------------')
    print(testClass1)
    print('\n')
    print(testClass1_tuple)
    print('---------------------')
    print('\n')

    print(' CLASS no. 3')
    print('---------------------')
    print(testClass3)
    print('\n')
    print(testClass3_tuple)
    print('---------------------')
    print('\n')

    data = testClass3

    print(' Type Map')
    print('---------------------')
    map = get_typemap(data)
    print(map)
    print('\n')
    print(' Type Map - Data')
    print('---------------------')
    print(map.data)
    print('\n')
    print(' Type Map - Type')
    print('---------------------')
    print(map.type)
    print('\n')

    print(' Type Map - Items')
    print('---------------------')
    for index in map.items:
        print(index)
        print('---------------------')
        print('\n')
        
        if type(index) is TypeMap:
            print(' Type Map - Sub-Items')
            print('---------------------')
            for sub in index.items:
                print(sub)
                print('---------------------')
                print('\n')

    

    
def debug():

    A = [11, 22 ,33]
    B = (4.0, 5.0, 6.0)
    C = [A, B]

    D = [88, 99]
    E = (3.14, 2.71)
    F  = (D, E)

    G = (C, F)
    H = (G, G)

    data = G

    print(data)
    print('\n')
    print('---------------------')

    map = get_structure_map_DC(data)
    print(map)
    print('\n')
    print('---------------------')

    # indata = tuple(A) + B + tuple(D) + E
    # print(indata)
    # print('\n')
    # print('---------------------')

    # unpacked_data = restructure(map, indata)
    # print(unpacked_data)
    # print('\n')
    # print('---------------------')

def test():

    A = [11, 22 ,33]
    B = (4.0, 5.0, 6.0)
    C = [A, B]

    D = [88, 99]
    E = (3.14, 2.71)
    F  = (D, E)

    G = (C, F)
    H = (G, G)

    data = F

    print(' Type Map')
    print('---------------------')
    map = get_typemap(data)
    print(map)
    print('\n')
    print(' Type Map - Data')
    print('---------------------')
    print(map.data)
    print('\n')
    print(' Type Map - Type')
    print('---------------------')
    print(map.type)
    print('\n')

    print(' Type Map - Items')
    print('---------------------')
   
    for index in map.items:
        print(index)
        print('---------------------')
        print('\n')
        
        if type(index) is TypeMap:
            print(' Type Map - Sub-Items')
            print('---------------------')
            for sub in index.items:
                print(sub)
                print('---------------------')
                print('\n')

# Main
# ------------------------------
if __name__ == "__main__":
    
    main()
    # debug()
    test()