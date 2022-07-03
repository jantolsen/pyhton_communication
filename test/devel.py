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
class StructureMap():
    type : type
    length : int
    items : list

@dataclass()
class TypeMap():
    """
    Type-Map Dataclass
    Class used for generation of Type-Structure map
    of a specified data-type (tuple, list, dataclass, etc.)
    This includes the: object, type and item-list
    Used with creating type-map and remapping datatype from type-map
    """
    data    : object
    type    : type
    items   : list

# Create Type-Map of Dataclass
def create_typemap_class(indata) -> TypeMap:
    """
    Create Type-Map of Dataclass
    Generates a TypeMap-dataclass containg the Type-Map structure
    of the incomming input-dataclass.
    Typically used for creating a type-map before packing dataclass 
    Note: the input-data needs to be a defined dataclass
    :param indata : Input Dataclass
    :return type_map : TypeMap-class of input-data type-structure
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
                        # _field_items.append(_elem_tuple)
                        _field_items.append(_elem_type)

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
                # _items.append(_item_tuple)
                _items.append(_field_type)
                
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
    Create Type-Map of Iterable-Type (list, tuple, etc.)
    Generates a TypeMap-class containing the Type-Map structure
    of the incomming input.
    Typically used for creating a type-map before packing data 
    Note: the input-data needs to be a iterable data-structured-type
    :param indata : Input data
    :return type_map : TypeMap-class of input-data type-structure
    """
    # Check if in-data is iterable
    if not is_iterable(indata):
        # Raise error
        raise TypeError('create_typemap_iter: ERROR - In-Data is NOT iterable, cannot create a type-map')

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
                                # _elem_items.append(_comp_tuple)
                                _elem_items.append(_comp_type)
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
                        # _field_items.append(_elem_tuple)
                        _field_items.append(_elem_type)
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
                # _items.append(_item_tuple)
                _items.append(_field_type)
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
    Get Type-Map of input-data
    Uses either "create_typemap_class"- or "create_typemap_iter"-function 
    to generate a TypeMap-class for the input-data
    Note: input-data needs to be a dataclass or a iterable structured type
    Typically used for creating a type-map before packing dataclass 
    :param indata : Input data 
    :return type_map : Type-Map structure of input-data
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

# Create a Re-Mapped Dataclass
def remap_from_typemap_class(indata, map : TypeMap):
    """
    """

# Create a Re-Mapped Iterable
def remap_from_typemap_iter(indata, map : TypeMap):
    """
    """

    # Check if in-data is iterable
    if not is_iterable(indata):
        # Raise error
        raise TypeError('remap_from_typemap_iter: ERROR - In-Data is NOT iterable, cannot peform re-mapping')

    # Continue Re-Mapping using input-iterable and Type-Map
    else:
        # Assign values to local variables based on in-data
        _data_list = []
        _type = map.type
        _index = 0  # Loop-index

        # Layer No. 1 - Iteration 
        # ------------------------------
        # Iterate through map-items
        for item in map.items:
            
            print('Layer - 1 - Loop {%s}' %(_index))
            print('---------------------')
            print(item)
            print('\n')

            # Layer No. 2 - Data
            # ------------------------------
            # Check if Item is a Type-Map
            if type(item) is TypeMap:
                print(' Item is TypeMap')
                print('\n')
                print('---------------------')

                _item_map = item
                _item_type = item.type
                _item_list = []
                
                # Layer No. 2 - Iteration
                # ------------------------------
                # Iterate through the elements of the item-map
                for elem in _item_map.items:
                    
                    print('Layer - 2 - Loop {%s}' %(_index))
                    print('---------------------')
                    print(elem)
                    print('\n')

                    # Layer No. 3 - Data
                    # ------------------------------
                    # Check if Element is a Type-Map
                    if type(elem) is TypeMap:
                        print(' Element is TypeMap')
                        print('\n')
                        print('---------------------')

                        _elem_map = elem
                        _elem_type = elem.type
                        _elem_list = []

                        # Layer No. 3 - Iteration
                        # ------------------------------
                        # Iterate through the components of the element-map
                        for comp in _elem_map.items:
                            
                            print('Layer - 3 - Loop {%s}' %(_index))
                            print('---------------------')
                            print(elem)
                            print('\n')

                            # Layer No. 4 - Data
                            # ------------------------------
                            # Check if component is a Type-Map
                            if type(comp) is TypeMap:
                                print(' Component is TypeMap')
                                print('\n')
                                print('---------------------')

                                _comp_map = comp
                                _comp_type = comp.type
                                _comp_list = []
                                
                                # Raise error
                                raise StopIteration('remap_from_typemap_iter: ERROR - Maximum nested layers exceeded')

                            # Component equals an Iterable-type
                            # Check if equal type is found in in-data at index 
                            elif (comp is type(indata[_index])):
                                print(' Component is Iterable-type')
                                print('\n')
                                print('---------------------')

                                # Update local data
                                _indata = indata[_index]    # Get in-data at index
                                _elem_list.append(_indata)  # Append in-data at index to element-list
                                _index += 1                 # Increment Loop-Index

                            # Error Handling
                            else:
                                raise TypeError(""" remap_from_typemap_iter: ERROR - Something went wrong. 
                                                    Iteration member {%s} does not equal TypeMap-dataclass 
                                                    nor equal the type of in-data at index #{%s} """%(comp, _index))
                        # ------------------------------
                        # End - Layer No. 3 Iteration

                        # Update Data
                        # ------------------------------
                        # Create Element-Data based on Type-Map entries and datatype
                        _elem_data = create_iter_type(_elem_list, _elem_type)
                        # Append Element-data to general Item-list   
                        _item_list.append(_elem_data)     

                    # Element equals an Iterable-type
                    # Check if equal type is found in in-data at index 
                    elif (elem is type(indata[_index])):
                        print(' Element is Iterable-type')
                        print('\n')
                        print('---------------------')

                        # Update local data
                        _indata = indata[_index]    # Get in-data at index
                        _item_list.append(_indata)  # Append in-data at index to item-list
                        _index += 1                 # Increment Loop-Index

                    # Error Handling
                    else:
                        raise TypeError(""" remap_from_typemap_iter: ERROR - Something went wrong. 
                                            Iteration member {%s} does not equal TypeMap-dataclass 
                                            nor equal the type of in-data at index #{%s} """%(elem, _index))
                # ------------------------------
                # End - Layer No. 2 Iteration
                
                # Update Data
                # ------------------------------
                # Create Item-Data based on Type-Map entries and datatype
                _item_data = create_iter_type(_item_list, _item_type)
                # Append Item-data to general data-list   
                _data_list.append(_item_data)                           

            # Item equals an Iterable-type
            # Check if equal type is found in in-data at index 
            elif (item is type(indata[_index])):
                print(' Item is Iterable-type')
                print('\n')
                print('---------------------')

                # Update local data
                _indata = indata[_index]    # Get in-data at index
                _data_list.append(_indata)  # Append in-data at index to data-list
                _index += 1                 # Increment Loop-Index

            # Error Handling
            else:
                raise TypeError(""" remap_from_typemap_iter: ERROR - Something went wrong. 
                                    Iteration member {%s} does not equal TypeMap-dataclass 
                                    nor equal the type of in-data at index #{%s} """%(item, _index))
            # ------------------------------
            # End - Layer No. 2 Data
        # ------------------------------
        # End - Layer No. 1 Iteration

        # Update Data
        # ------------------------------
        # Create data based on Type-Map entries and datatype
        data = create_iter_type(_data_list, _type)

        print('---------------------')
        print(' End of Remapping ')
        print('\n')
        print('---------------------')
    # Function return
    return data

# Create Iterable Type 
def create_iter_type(indata : list, iter_type : type):
    """
    Create Iterable Type based on input-data and input-type
    Used in conjunction with re-mapping from type-map
    Input-data is converted to the correct iterable type 
    """
    # Input-data should be a List
    if iter_type is list:
        data = indata

    # Input-data should be a tuple
    elif iter_type is tuple:
        data = tuple(indata)

    # Error
    else:
        # Raise error
        raise TypeError('create_iter_type: ERROR - Unknown iterable data-type-structure')

    # Function return
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

def debug():

    A = [11, 22 ,33]
    B = (4.0, 5.0, 6.0)
    C = [A, B]

    D = [88, 99]
    E = (3.14, 2.71)
    F  = (D, E)

    G = (C, F)
    H = ((A, D), (E), (D, A))

    data = H

    print(' DATA ')
    print('---------------------')
    print(data)
    print('\n')
    print('---------------------')
    print('\n')

    # -----------------------------
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
    # -----------------------------

    raw_C = tuple(A) + B
    raw_F = tuple(D) + E 
    raw_G = raw_C + raw_F
    
    raw_H = tuple(A) + tuple(D) + E + tuple(D) + tuple(A)



    raw_data = raw_H
    # raw_data = tuple(B)

    print(' Raw-data ')
    print('---------------------')
    print(raw_data)
    print('\n')
    print('---------------------')

    print(' Re-Mapping ')
    print('---------------------')
    remapped_data = remap_from_typemap_iter(raw_data, map)
    print(remapped_data)
    print('\n')
    print('---------------------')

    print(' Comparison ')
    print('---------------------')
    print(' Raw-data ')
    print(data)
    print('\n')
    print(' Remapped-data ')
    print(remapped_data)
    print('---------------------')


    # print(' DATA ')
    # print('---------------------')
    # print(' Structured data ')
    # print(data)
    # print('\n')
    # print(' Raw-data ')
    # print(raw_data)
    # print('---------------------')

# Main
# ------------------------------
if __name__ == "__main__":
    
    # main()
    
    # test()

    debug()