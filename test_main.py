# Communication Main
# ------------------------------
# Description:
# Main script for communication package

# Version
# ------------------------------
# 0.0   -   Initial version
#           [12.07.2022] - Jan T. Olsen

# Import packages
from dataclasses import dataclass, field, fields, is_dataclass
import pickle

# Import Toolbox
import comm_toolbox as CommToolbox

# Import Class Files
from lib.generic_commdata import GenericCommClass
from comm_data import TestClass1

@dataclass
class TestClass2(GenericCommClass):
    name : str = 'olsen'
    age : int = 12
    heigth : float = 1.70
    lista_mi : list = field(default_factory=list)

@dataclass
class TestClass3(GenericCommClass):
    class1 : TestClass1
    class2 : TestClass2

@dataclass
class TestClass6(GenericCommClass):
    
    verdi : float
    class3 : TestClass3
    class1 : TestClass1

    

def test():
    # ------------------------------
    testClass1 = TestClass1()
    testClass2 = TestClass2(lista_mi=[1.852, 77.0, 995.0])
    testClass3 = TestClass3(testClass1, testClass2)
    testClass6 = TestClass6(0.909, testClass3, testClass1)

    # ------------------------------
    new_data_1 = TestClass1(456.675, 995)
    new_data_2 = TestClass2('jens', 35, 1.92, [99.0, 88.0, 77.0])
    new_data_3 = TestClass3(new_data_1, new_data_2)
    new_data_6 = TestClass6(808.8, new_data_3, new_data_1)
    # ------------------------------

    data = testClass6
    new_data = new_data_6

    # ------------------------------
    print('\n')
    print(' DATA ')
    print('---------------------')
    print(data)
    print('---------------------')
    print('\n')

    # ------------------------------
    print(' Map Generation ')
    print('---------------------')
    print('\n')

    print('     Type Map')
    print('     ---------------------')
    map = data.type_map
    print(map)
    print('\n')

    print('     Type Map - Data')
    print('     ---------------------')
    print(map.data)
    print('\n')

    print('     Type Map - Type')
    print('     ---------------------')
    print(map.type)
    print('\n')

    print('     Type Map - Items')
    print('     ---------------------')
    print(map.items)
    print('\n')

    for index in map.items:

        print('         Item in Map Items')
        print(index)
        print('         ---------------------')
        print('\n')

        if type(index) is CommToolbox.TypeMap:

            print('             Sub-Item in Map Items')
            print(index.items)
            print('             ---------------------')
            print('\n')
    
    # -----------------------------------------

    # ------------------------------
    print(' Byte Packing ')
    print('---------------------')
    packed_dataclass, conversion_code = new_data.pack_to_bytes()
    print('\n')

    print('     Packed Dataclass')
    print('     ---------------------')
    print(packed_dataclass)
    print('\n')

    print('     Conversion Code')
    print('     ---------------------')
    print(conversion_code)
    print('\n')

    print(data.get_byte_conversion())
    print('\n')

    
    # ------------------------------
    print('\n')
    print(' Original Data: ')
    print('---------------------')
    print(data)
    print('---------------------')
    print('\n')

    print('\n')
    print(' Remap from Bytes ')
    print('---------------------')
    unpacked_data = data.remap_from_bytes(packed_dataclass, conversion_code)
    print('\n')
    print('     Unpacked data:')
    print(unpacked_data)
    print('\n')
    print('     Remapped data:')
    print(data)
    print('---------------------')
    print('\n')

def test2():
    # ------------------------------
    A = [11, 22 ,33]
    B = (4.0, 5.0, 6.0)
    C = [A, B]

    D = [88, 99]
    E = (3.14, 2.71)
    F  = (D, E)

    G = (C, F)
    H = (12, G, 0.23, C)

    I = [G, H]

    X = 8
    # ------------------------------

    data = C

    # ------------------------------
    print('\n')
    print(' DATA ')
    print('---------------------')
    print(data)
    print('---------------------')
    print('\n')
    # ------------------------------

    # ------------------------------
    conv_code = CommToolbox.get_byte_conversion(data)
    print('\n')
    print(' Conversion Code ')
    print('---------------------')
    print(conv_code)
    print('---------------------')
    print('\n')

    # ------------------------------
    packed_data, conv_code, flat_data = CommToolbox.pack_to_bytes(data)
    print('\n')
    print(' Pack 2 Bytes ')
    print('---------------------')
    print('     Packed data:')
    print(packed_data)
    print('\n')
    print('     Conversion Code:')
    print(conv_code)
    print('\n')
    print('     Flat data:')
    print(flat_data)
    print('---------------------')
    print('\n')
    # ------------------------------


@dataclass
class TestClass10():
    nautisk_mil : float = 1.852
    engelsk_mil : int = 1609 

@dataclass
class TestClass11():
    name : str = 'olsen'
    age : int = 12
    heigth : float = 1.70
    lista_mi : list = field(default_factory=list) 

@dataclass
class TestClass12():
    
    verdi : float
    class3 : TestClass10
    class1 : TestClass11

def test3():

    testClass10 = TestClass10()
    testClass11 = TestClass11(lista_mi=[1.852, 77.0, 995.0])
    testClass12 = TestClass12(4638.8, testClass10, testClass11)


    data = testClass12
    # ------------------------------
    print('\n')
    print(' DATA ')
    print('---------------------')
    print(data)
    print('---------------------')
    print('\n')

    print('\n')
    print(' Packed ')
    print('---------------------')
    packed_data = pickle.dumps(data)
    print(len(packed_data)) 
    print(type(packed_data)) 
    print('\n')
    print(packed_data)
    print('---------------------')
    print('\n')

    print('\n')
    print(' UnPacked ')
    print('---------------------')
    unpacked_data = pickle.loads(packed_data)
    print(unpacked_data)
    print('---------------------')
    print('\n')

# Main
# ------------------------------
if __name__ == "__main__":

    # test()

    # test2()

    test3()