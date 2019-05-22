## @ingroup Analyses-Weights
# Weights_Supersonic_UAV.py
#
# Created: May 2019, B. Dalman

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

import SUAVE
from SUAVE.Core import Data
from .Weights import Weights


# ----------------------------------------------------------------------
#  Analysis
# ----------------------------------------------------------------------

## @ingroup Analyses-Weights
class Weights_Supersonic_UAV(Weights):
    """ This is class that evaluates the weight of a supersonic UAV
    
    Assumptions:
        None

    Source:
        N/A

    Inputs:
        None
      
    Outputs:
        None

    Properties Used:
        N/A
    """
    def __defaults__(self):
        """This sets the default values and methods for the UAV weight analysis.
    
        Assumptions:
        None

        Source:
        N/A

        Inputs:
        None

        Outputs:
        None

        Properties Used:
        N/A
        """           
        self.tag = 'weights_supersonic_uav'
        
        self.vehicle  = Data()
        self.settings = Data()
        
        
    def evaluate(self,conditions=None):
        """Evaluate the weight analysis.
    
        Assumptions:
        None

        Source:
        N/A

        Inputs:
        None

        Outputs:
        results

        Properties Used:
        N/A
        """         
        # unpack
        vehicle = self.vehicle
        buildup   = SUAVE.Methods.Weights.Buildups.Common.uav_buildup     

        max_thrust = vehicle.turbojet.thrust.total_design

        # evaluate
        results = buildup(vehicle, max_thrust)
        
        # storing weigth breakdown into vehicle
        vehicle.weight_breakdown = results 

        # updating empty weight
        vehicle.mass_properties.operating_empty = results.empty
              
        # done!
        return results
    
    
    def finalize(self):
        """Finalize the weight analysis.
    
        Assumptions:
        None

        Source:
        N/A

        Inputs:
        None

        Outputs:
        None

        Properties Used:
        N/A
        """           
        self.mass_properties = self.vehicle.mass_properties
        
        return
