## @ingroup Attributes-Atmospheres-Earth
#Wind_Tunnel.py

# Created:  June 2020, B. Dalman

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

import numpy as np
from SUAVE.Attributes.Gases import Air
from SUAVE.Attributes.Atmospheres import Atmosphere
from SUAVE.Attributes.Planets import Earth
from SUAVE.Core import Data
from SUAVE.Core import Units

# ----------------------------------------------------------------------
#  Wind_Tunnel Atmosphere Class
# ----------------------------------------------------------------------
## @ingroup Attributes-Atmospheres-Earth
class Wind_Tunnel(Atmosphere):
    """Contains NTP values for all altitudes. Easy to update values based off given experimental data. Comments also mention important parts about Re number calcs.
    
    Assumptions:
    None
    
    Source:
    For use to V&V individual papers
    """
    
    def __defaults__(self):
        """This sets the values for calculations at easily customizable atmospheric conditions.

        Assumptions:
        None

        Source:
        None

        Inputs:
        None

        Outputs:
        None

        Properties Used:
        None
        """          
        self.tag = 'Wind Tunnel'

        # break point data: 
        self.fluid_properties = Air()
        self.planet = Earth()
        self.breaks = Data()
        self.breaks.altitude    = np.array( [0.00]) * Units.km     # m, geopotential altitude


        self.temperature        = np.array( [293.15] ) # K
        self.pressure           = np.array( [101325.0] ) # Pa
        #self.density            = np.array( [1.20411e0] ) # kg/m^3