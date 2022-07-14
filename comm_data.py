# Communication Data
# ------------------------------
# Description:
# Predefined Communication Data to be used 
# with an communication connection
# (transfer and receive)

# Version
# ------------------------------
# 0.1   -   Updated with Generic-Communication-Dataclass
#           [12.07.2022] - Jan T. Olsen 
# 0.0   -   Initial version
#           [30.06.2022] - Jan T. Olsen

# Import packages
from dataclasses import dataclass, field, fields, is_dataclass

# Import Toolbox
import comm_toolbox as CommToolbox

# Import Class Files
from lib.generic_commdata import GenericCommClass

# Dataclass - Test-Class
@dataclass
class TestClass1(GenericCommClass):

    nautisk_mil : float = 1.852
    engelsk_mil : int = 1609 