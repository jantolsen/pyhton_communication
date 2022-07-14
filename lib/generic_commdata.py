# Generic Communication Data-Class
# ------------------------------
# Description:
# Parent dataclass for Communication dataclasses
# with related functions related to type-map
# pack- and unpacking to and from bytes,

# Version
# ------------------------------
# 0.1   -   Updated with pack and unpack to 
#           and from bytes
#           [14.07.2022] - Jan T. Olsen 
# 0.1   -   Updated with features related 
#           to Type-Map and remapping
#           [12.07.2022] - Jan T. Olsen 
# 0.0   -   Initial version
#           [30.06.2022] - Jan T. Olsen

# Import packages
from dataclasses import dataclass, field, fields, is_dataclass

# Import Toolbox
import comm_toolbox as CommToolbox

# Dataclass - Generic Communication Dataclass
@dataclass()
class GenericCommClass():
    """
    Generic Communication Dataclass
    Acts as a Parent class for inherited Communication dataclasses
    This dataclass contains data on the Type-Structure-Map, and functions
    related to generating the type-map, remapping/updating the dataclass
    attributes, finding the Byte-Conversion-Code, aswell as packing and unpacking
    the Data-Class to and from bytes (respectively)
    """

    # Dataclass Type-Map
    type_map : CommToolbox.TypeMap = field(init=False, default_factory=CommToolbox.TypeMap, repr=False)

    # Post Initialization
    # ------------------------------
    def __post_init__(self):
        # Get and Assign Class Type-Map using "get_map"-function
        self.type_map = self.get_typemap()

    # Get Type-Map
    # ------------------------------
    def get_typemap(self) -> CommToolbox.TypeMap:
        """
        Get Type-Map
        Iterate through the dataclass attributes and generates 
        a Type-Structure-Map of the related dataclass.
        :param self : Dataclass object
        :return TypeMap : Dataclass Type-Map 
        """

        # Define and assign values to local variables based self-dataclass object
        _data = self
        _type = type(_data)
        _items = []
        _size = 0

        # Iterate through the fields of the dataclass
        for field in fields(self):

            # Get the data of current field
            _field_name = field.name
            _field_data = self.__getattribute__(_field_name)
            _field_type = type(_field_data)
            _field_length = len(_field_data) if CommToolbox.is_iterable(_field_data) else 1

            # Field is a Type-Map
            # ------------------------------ 
            if _field_type is CommToolbox.TypeMap:
                # Skip if field is a Type-Map
                pass
            
            # Field-data is a dataclass
            # ------------------------------ 
            elif is_dataclass(_field_data):
                # Get Type-Map of Dataclass
                _field_map = _field_data.type_map

                # Create a data-tuple on current field 
                _item_tuple = (_field_map, _field_length)

                # Append data-tuple of current field to item-list
                _items.append(_item_tuple)
                # _items.append(_field_map)

                # Update Size
                _size += _field_map.size

            # Field-data is Iterable-Type 
            # ------------------------------ 
            # (list, tuple, etc.)
            elif (_field_type is tuple) or (_field_type is list):
                # Create a data-tuple on current field 
                _item_tuple = (_field_type, _field_length)

                # Append data-tuple of current field to item-list
                _items.append(_item_tuple)
                # _items.append(_field_type)

                # Update Size
                _size += _field_length

            # Field-data is Primitive Type
            # ------------------------------ 
            # (int, float, string, etc.)
            else:
                # Create a data-tuple on current field 
                _item_tuple = (_field_type, _field_length)
                
                # Append data-tuple of current field to item-list
                _items.append(_item_tuple)
                # _items.append(_field_type)

                # Update Size
                _size += _field_length

        # Creat a Type-Map object of obtained data
        type_map = CommToolbox.TypeMap(_data, _type, _items, _size)

        # Function return
        return type_map

    # Get Byte Conversion Code
    # ------------------------------
    def get_byte_conversion(self) -> str:
        """
        Find the Byte Conversion-Code of the dataclass
        Searches through the attributes and uses the 
        "CommToolbox.get_byte_conversion"-function to generate a
        byte conversion code
        :param self: Dataclass object
        :return conversion_code: Byte Conversion-Code of dataclass (str)
        """

        # Define Byte Conversion-Code variable
        conversion_code = ''

        # Iterate through the fields of the dataclass
        for field in fields(self):

            # Get the data of current field
            _field_name = field.name
            _field_data = self.__getattribute__(_field_name)
            _field_type = type(_field_data)
            _field_length = len(_field_data) if CommToolbox.is_iterable(_field_data) else 1

            # Field is a Type-Map
            # ------------------------------ 
            if _field_type is CommToolbox.TypeMap:
                # Skip if field is a Type-Map
                pass
            
            # Field-data is a dataclass
            # ------------------------------ 
            elif is_dataclass(_field_data):
                # Call "pack_to_bytes"-function of the Field-data dataclass
                field_conversion_code = _field_data.get_byte_conversion()
                
                # Update ConversionCode with data from current field-dataclass 
                conversion_code += field_conversion_code

            # Field-data is Iterable or Primitive Type
            # ------------------------------ 
            # (int, float, string, etc.)
            else:
                # Get Item's Byte-Conversion-Code
                _item_conversion_code = CommToolbox.get_byte_conversion(_field_data)

                # Add Conversion-Code for Item
                conversion_code += _item_conversion_code

        # Return Conversion-Code
        return conversion_code

    # Remap Dataclass
    # ------------------------------
    def remap_dataclass(self, indata) -> object:
        """
        Remap dataclass
        Incomming flat structured data is used together with the
        dataclass Type-Map to update and remap the attributes of
        the governing dataclass
        :param indata : Flat structured data to update the class
        :return self : Updated Dataclass Object 
        """

        # Define and assign values to local variables based on Type-Map
        _data_list = []
        _new_dataclass = self.type_map.type 
        _index = 0  # Loop-index
        _size = self.type_map.size

        # Iterate through Map-Items
        # (Map-Items is defined as a list)
        for item in self.type_map.items:

            _item_type = item[0]    # First entry equals the Type
            _item_len = item[1]     # Second entry equals the length of the Type
            _item_list = []         # Define a Item-list

            # Item is a Type-Map
            # ------------------------------
            # (Nested dataclasses)
            if type(_item_type) is CommToolbox.TypeMap:

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

                # Call remap for Sub-Dataclass
                _sub_dataclass = _sub_data.remap_dataclass(_sub_indata)

                # Update loop-index
                _index += _sub_items_size

                # Append Sub-Dataclass to data-list
                _data_list.append(_sub_dataclass)

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

        # Convert and Update Dataclass
        # ------------------------------
        _data_tuple = tuple(_data_list)                 # Convert data-list to a tuple (easier to apply entries for a dataclass)
        _new_dataclass = _new_dataclass(*_data_tuple)   # Unpack tuple to new dataclass

        # Update data-class with local defined variable

        # Iterate through the fields of the original dataclass
        for field in fields(self):
            # Get the name of current field
            _field_name = field.name
            
            # Check if New-Dataclass has the field-name of the original dataclass
            if hasattr(_new_dataclass, _field_name):
                # Get field attribute of the related field-name of the New-Dataclass 
                _field_data = _new_dataclass.__getattribute__(_field_name)
                # Assign attribute from the New-Dataclass to the original dataclass
                setattr(self, _field_name, _field_data)

        # Function return
        return _new_dataclass

    # Pack Dataclass to Bytes
    # ------------------------------
    def pack_to_bytes(self) -> tuple[bytes, str]:
        """
        Pack the Dataclass to Bytes
        Get data entries from dataclass and pack them to bytes with correct 
        conversion-code for the related data-types
        Packed-data can be used for data-transfer over TCP/UDP
        :return packed_dataclass: Packed Dataclass data (bytes)
        :return conversion_code: Dataclass Conversion-Code (str)
        """
        # Define data to be packed as list
        packed_dataclass = b''
        conversion_code = ''    

        # Iterate through the fields of the dataclass
        for field in fields(self):

            # Get the data of current field
            _field_name = field.name
            _field_data = self.__getattribute__(_field_name)
            _field_type = type(_field_data)
            _field_length = len(_field_data) if CommToolbox.is_iterable(_field_data) else 1

            # Field is a Type-Map
            # ------------------------------ 
            if _field_type is CommToolbox.TypeMap:
                # Skip if field is a Type-Map
                pass
            
            # Field-data is a dataclass
            # ------------------------------ 
            elif is_dataclass(_field_data):
                # Call "pack_to_bytes"-function of the Field-data dataclass
                field_packed_data, field_conversion_code = _field_data.pack_to_bytes()
                
                # Update Packed Dataclass and ConversionCode with data from current field-dataclass 
                packed_dataclass += field_packed_data
                conversion_code += field_conversion_code

            # Field-data is Iterable or Primitive Type
            # ------------------------------ 
            # (int, float, string, etc.)
            else:
                # Pack Field-Data to bytes
                # (using "CommToolbox.pack_to_byes"-function)
                field_packed_data, field_conversion_code, field_data = CommToolbox.pack_to_bytes(_field_data)

                # Update Packed Dataclass and ConversionCode with data from current field-data
                packed_dataclass += field_packed_data
                conversion_code += field_conversion_code
    
        # Function return
        return packed_dataclass, conversion_code

    # Remap Dataclass from Bytes
    # ------------------------------
    def remap_from_bytes(self, packed_dataclass : bytes, conversion_code : str):
        """
        Remap Dataclass from Bytes
        Packed-dataclass (bytes) is used together with the conversion-code 
        and the class Type-Map to update the attributes of the governing dataclass
        :param packed_dataclass : Packed Dataclass (bytes)
        :param conversion_code : Byte-Conversion-Code (str)
        :return self : Updated Dataclass Object 
        :return unpacked_dataclass : Unpacekd Dataclass Object (flat-structured) 
        """

        # Unpack Dataclass from bytes
        # (this will create "flat-structured"-data of the dataclass attributes)
        unpacked_dataclass = CommToolbox.unpack_from_bytes(packed_dataclass, conversion_code)

        # Remap Dataclass using the Unpacked Dataclass (flat-structured)
        self.remap_dataclass(unpacked_dataclass)

        # Function return
        return unpacked_dataclass