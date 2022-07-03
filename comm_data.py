# Communication Data
# ------------------------------
# Description:
# Predefined Communication Data
# to be used with an communication connection
# (transfer and receive)

# Version
# ------------------------------
# 0.0   -   Initial version
#           [30.06.2022] - Jan T. Olsen

# Import packages
from dataclasses import dataclass, field, fields, is_dataclass
import struct

# Import Toolbox
import comm_toolbox as CommToolbox

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
            conversioncode += CommToolbox.get_conversioncode(_value)

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
        packed_dataclass = b''
        conversioncode = '' 
        data : list = []    

        # Iterate through the fields of the dataclass
        for field in fields(self):
            # Get data for current field
            _name = field.name
            _value = self.__getattribute__(_name)
            _type = type(_value)
            
            # Pack Data to Bytes
            # (Call "CommToolbox.pack_to_bytes()")
            _packed_data, _conversioncode, _data = CommToolbox.pack_to_bytes(_value)

            # Update Packed Dataclass and ConversionCode with data from current field 
            packed_dataclass += _packed_data
            conversioncode += _conversioncode

            # # Check if date of current field is a dataclass
            # if is_dataclass(_type):
            #     # Raise error
            #     raise TypeError('ERROR: _CommDataclass.pack_to_bytes: To many nested layers of Indata')

            # # Special case: String
            # if type(_value) is str:
            #     # String needs to be encoded to byte-value
            #     _value = _value.encode('UTF-8')
            
            # # Append acquired information to arrays
            # data.append(_value)

        # # Get Dataclass Conversion-Code
        # conversioncode = self.get_conversioncode()

        # # Pack Dataclass data to byte
        # packed_dataclass = struct.pack(CommToolbox._COMM_CONST.Network + conversioncode, *data)


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
            unpacked_dataclass = CommToolbox.unpack_from_bytes(packed_dataclass, conversioncode)

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
class GamepadJoystick(_CommDataclass):
    """
    Dataclass for Gamepad Joystick Communication:
    Predefined Dataclass for a Gamepad Joystick communication.
    Inherits from the generic Communication-Dataclass (_CommDataClass)
    :param id: Identification/Name of joystick (str)
    :param X: X-Axis value (float)
    :param Y: Y-Axis value (float)
    :param PB: Pushbutton value (bool)
    """
    id : str    
    X : float = 0.0
    Y : float = 0.0
    PB : bool = False

@dataclass
class GamepadTrigger(_CommDataclass):
    """
    Dataclass for Gamepad Trigger Communication:
    Predefined Dataclass for a Gamepad Trigger communication.
    Inherits from the generic Communication-Dataclass (_CommDataClass)
    :param id: Identification/Name of Trigger (str)
    :param val: Trigger value (float)
    :param B1: Back Bumper No. 1 (bool)
    :param PB: Back Bumper No. 1 (bool)
    """
    id : str    
    val : float = 0.0
    B1 : bool = False
    B2 : bool = False

@dataclass
class Axis():
    """
    Dataclass for Axis:
    Predefined Dataclass for an Axis.
    :param id: Identification/Name of Axis (str)
    :param pos: Axis Posiiton (float)
    :param vel: Axis Velocity (float)
    :param acc: Axis Acceleration (float)
    """
    id : str = 'Axis_No'    
    pos : float = 0.0
    vel : float = 0.0
    acc : float = 0.0

@dataclass
class Machine(_CommDataclass):
    Axis1 : Axis #= field(init=True, default_factory = Axis)
    Axis2 : Axis #= field(init=True, default_factory = Axis)

@dataclass
class TestClass_1(_CommDataclass):
    byte_code : bytes = field(init=False, repr=False)
    name : str = 'jan'
    # age : int = 29
    age : list = field(init=False, default_factory = list)
    heigth : float = 1.85
    

    def __post_init__(self):
        self.byte_code = self.name.encode('UTF-8')
        self.age.append(11)
        self.age.append(4224)

@dataclass
class TestClass_2(_CommDataclass):
    name : str = 'olsen'
    # age : bool = False
    age : list = field(init=False, default_factory = list)
    # age : list[22,33]
    heigth : float = 1.70

    def __post_init__(self):
        self.age.append(33)
        self.age.append(44)


# Main function
def main():
    q1 = Axis(id='Q1', pos=45.0)
    q2 = Axis(id='Q2', pos=-10.0, vel=5.0)

    # PDS = Machine(q1, q2)

    # print(PDS)
    # # print(PDS.get_conversioncode())
    # print('\n')

    # packedData, convCode = PDS.pack_to_bytes()
    # print(packedData)
    # print(convCode)
    # print('\n')

    # PDS.unpack_from_bytes(packedData, convCode)
    # print(PDS)
    # print('\n')

    # print(type(q1))
    # print('\n')

    # if CommToolbox._iterable(PDS):
    #     print('is a iterable')
        
    # else:
    #     print('Not iterable')
    # print('\n')

    # if is_dataclass(PDS):
    #     print('is a class')
        
    # else:
    #     print('Not a class')
    # print('\n')

    tupleA = [11, 22 ,33]
    tupleB = (4.0, 5.0, 6.0)
    tupleC = ('jan', 18, 9.9, False)
    tupleD = [tupleA, tupleB, tupleC, 2]
    tupleE = (tupleA, tupleB, q1, 2)

    print(tupleE)
    print('\n')
    print('---------------------')

    # abc = {}
    # for item in tupleD:
    #     print(item)

    #     type_name = type(item).__name__

    #     abc[type_name] = (type_name, item)

    #     if CommToolbox._iterable(item):

    #         for element in item:

    #             type_name = type(element).__name__

    #             abc[type_name] = (type_name, element)

    # if is_dataclass(q1):

    #     print(q1)

    print('---------------------')

    if CommToolbox._iterable(tupleE):

        for item in tupleE:
            if CommToolbox._iterable(item):
                type_name = type(item).__name__
                print(item)
                print(type_name)
                print(len(item))
                
            else:
                type_name = type(item).__name__
                print(item)
                print(type_name)
            print('---------------------')
            print('\n')

            # if item is dataclass:
            #     print(item)

            # if item is tuple or list or set:
            if CommToolbox._iterable(item):

                for element in item:
                    if CommToolbox._iterable(element):
                        type_name = type(element).__name__
                        print(element)
                        print(type_name)
                        print(len(element))
                        
                    else:
                        type_name = type(element).__name__
                        print(element)
                        print(type_name)
                    
                    print('\n')
            print('---------------------')


    #     print('\n')
        
    # print('\n')

    # print(abc)

    # print(tupleD)
    # print(type(tupleD[0]))
    # print('\n')

    # packed_data, convcode = CommToolbox.pack_to_bytes(tupleD)
    # print(packed_data)
    # print(convcode)
    # print('\n')

    # unpacked_data = CommToolbox.unpack_from_bytes(packed_data, convcode)
    # print(unpacked_data)
    # print('\n')


def test_debug():

    data_test1= TestClass_1()
    print(data_test1)
    # print(data_test1.get_conversioncode())
    print(data_test1.byte_code)
    print('\n')

    # data_test2 = TestClass_2()
    # print(data_test2)
    # print(data_test2.get_conversioncode())
    # print('\n')

    # packedData, convCode = data_test1.pack_to_bytes()
    # print(packedData)
    # print(convCode)
    # print('\n')

    # data_test2.unpack_from_bytes(packedData, convCode)
    # print(data_test2)
    # print('\n')

# Main
# ------------------------------
if __name__ == "__main__":

    main()

    # test_debug()


