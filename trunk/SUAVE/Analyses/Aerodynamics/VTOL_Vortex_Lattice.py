## @ingroup Analyses-Aerodynamics
# VTOL_Vortex_Lattice.py
#
# Created:  Jan 2018, M. Clarke

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# SUAVE imports
import SUAVE

from SUAVE.Core import Data
from SUAVE.Core import Units
from SUAVE.Methods.Aerodynamics.Common.Fidelity_Zero.Lift import vtol_weissinger_vortex_lattice

# local imports
from .Aerodynamics import Aerodynamics

# package imports
import numpy as np


# ----------------------------------------------------------------------
#  Class
# ----------------------------------------------------------------------
## @ingroup Analyses-Aerodynamics
class VTOL_Vortex_Lattice(Aerodynamics):
    """This builds a surrogate and computes lift using a basic vortex lattice.

    Assumptions:
    None

    Source:
    None
    """ 
     
    def __defaults__(self):
        """This sets the default values and methods for the analysis.

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
        self.tag = 'Vortex_Lattice'

        self.geometry = Data()
        self.settings = Data()

        # correction factors
        self.settings.fuselage_lift_correction           = 1.14
        self.settings.trim_drag_correction_factor        = 1.02
        self.settings.wing_parasite_drag_form_factor     = 1.1
        self.settings.fuselage_parasite_drag_form_factor = 2.3
        self.settings.aircraft_span_efficiency_factor    = 0.78
        self.settings.drag_coefficient_increment         = 0.0000        
        self.index = 0

    def evaluate(self,state,settings,geometry):
        # unpack
        conditions = state.conditions
        propulsors = geometry.propulsors
        vehicle_reference_area = geometry.reference_area
        total_lift_coeff = Data()
                
        n = state.numerics.number_control_points
        wing_CL = np.zeros((n,1))
        total_lift_coeff = np.zeros((n,1))
        
        # inviscid lift of wings only
        inviscid_wings_lift                                                    = Data()
        inviscid_wings_lift.total                                              = total_lift_coeff
        conditions.aerodynamics.lift_breakdown.inviscid_wings_lift             = Data()
        state.conditions.aerodynamics.lift_coefficient_wing                    = Data()
       
        for wing in geometry.wings.keys():
            for index in range(n):
                [wing_lift_coeff,  wing_drag_coeff ]                         = vtol_weissinger_vortex_lattice(conditions,settings,geometry.wings[wing],propulsors,index)
                wing_CL[index]                                               = wing_lift_coeff 
            inviscid_wings_lift[wing]                                        = wing_CL
            conditions.aerodynamics.lift_breakdown.inviscid_wings_lift[wing] = inviscid_wings_lift[wing]   
            state.conditions.aerodynamics.lift_coefficient_wing[wing]        = inviscid_wings_lift[wing]   
            total_lift_coeff                                                 += wing_CL * geometry.wings[wing].areas.reference / vehicle_reference_area  
                       
        conditions.aerodynamics.lift_breakdown.inviscid_wings_lift.total = total_lift_coeff
        state.conditions.aerodynamics.lift_coefficient                   = total_lift_coeff
        state.conditions.aerodynamics.inviscid_lift                      = total_lift_coeff 
        inviscid_wings_lift.total                                        = total_lift_coeff            
            
        return inviscid_wings_lift
    

    #def evaluate(self,state,settings,geometry):
        ## unpack
        #conditions = state.conditions
        #propulsors = geometry.propulsors
        #vehicle_reference_area = geometry.reference_area
        #total_lift_coeff = 0
        #total_drag_coeff = 0

        ## inviscid lift of wings only
        #inviscid_wings_lift                                                     = Data()
        #inviscid_wings_lift_distribution                                        = Data()
        #inviscid_wings_lift.total                                               = Data()
        #conditions.aerodynamics.lift_breakdown.inviscid_wings_lift              = Data()
        #conditions.aerodynamics.lift_breakdown.inviscid_wings_lift_distribution = Data()
        #conditions.aerodynamics.lift_breakdown.inviscid_wings_lift.total        = Data()
        #state.conditions.aerodynamics.lift_coefficient                          = Data()
        #state.conditions.aerodynamics.lift_coefficient_wing                     = Data() 
        #for wing in geometry.wings.values():
            #[wing_lift_coeff, wing_CL_distribution, wing_drag_coeff, wing_CD_distribution]     = vtol_weissinger_vortex_lattice(conditions,settings,wing,propulsors,self.index)
            #inviscid_wings_lift[wing.tag]                                                      = wing_lift_coeff 
            #inviscid_wings_lift_distribution[wing.tag]                                         = wing_CL_distribution  
            #conditions.aerodynamics.lift_breakdown.inviscid_wings_lift[wing.tag]               = inviscid_wings_lift[wing.tag]
            #conditions.aerodynamics.lift_breakdown.inviscid_wings_lift_distribution[wing.tag]  = inviscid_wings_lift_distribution[wing.tag]               
            #state.conditions.aerodynamics.lift_coefficient_wing[wing.tag]                      = inviscid_wings_lift[wing.tag]   
            #total_lift_coeff                                                                   += wing_lift_coeff * wing.areas.reference / vehicle_reference_area  

        #conditions.aerodynamics.lift_breakdown.inviscid_wings_lift.total = total_lift_coeff
        #state.conditions.aerodynamics.lift_coefficient                   = total_lift_coeff
        #state.conditions.aerodynamics.inviscid_lift                      = total_lift_coeff 
        #inviscid_wings_lift.total                                        = total_lift_coeff

        #self.index = self.index + 1        
        #if self.index == 15:
            #self.index = 0

        #return inviscid_wings_lift    