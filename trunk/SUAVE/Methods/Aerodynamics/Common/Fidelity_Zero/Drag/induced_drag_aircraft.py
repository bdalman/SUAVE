## @ingroup Methods-Aerodynamics-Common-Fidelity_Zero-Drag
# induced_drag_aircraft.py
# 
# Created:  Dec 2013, SUAVE Team
# Modified: Jan 2016, E. Botero
#           Apr 2020, M. Clarke       

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# suave imports
from SUAVE.Core import Data

# package imports
import numpy as np

# ----------------------------------------------------------------------
#  Induced Drag Aircraft
# ----------------------------------------------------------------------

## @ingroup Methods-Aerodynamics-Common-Fidelity_Zero-Drag
def induced_drag_aircraft(state,settings,geometry):
    """Determines induced drag for the full aircraft

    Assumptions:
    Based on fits

    Source:
    adg.stanford.edu (Stanford AA241 A/B Course Notes)

    Inputs:
    state.conditions.aerodynamics.lift_coefficient               [Unitless]
    state.conditions.aerodynamics.drag_breakdown.parasite.total  [Unitless]
    configuration.oswald_efficiency_factor                       [Unitless]
    configuration.viscous_lift_dependent_drag_factor             [Unitless]
    geometry.wings['main_wing'].span_efficiency                  [Unitless]
    geometry.wings['main_wing'].aspect_ratio                     [Unitless]

    Outputs:
    total_induced_drag                                           [Unitless]

    Properties Used:
    N/A
    """

    # unpack inputs
    conditions    = state.conditions
    configuration = settings
    
    K       = configuration.viscous_lift_dependent_drag_factor
    CDp     = state.conditions.aerodynamics.drag_breakdown.parasite.total
    CL      = conditions.aerodynamics.lift_coefficient
    e       = configuration.oswald_efficiency_factor	
    CDi_inv = conditions.aerodynamics.drag_breakdown.induced.total
    wing_e  = geometry.wings['main_wing'].span_efficiency     
    ar      = geometry.wings['main_wing'].aspect_ratio
     
    # Inviscid osward efficiency factor
    if wing_e  == None:
        wing_e  = CL**2/(CDi_inv*np.pi*ar)
    else:
        CDi_inv = CL**2/(wing_e *np.pi*ar)  
        
    # Fuselage correction for induced drag (insicid + viscous)
    if e == None:	
        e = 1/((1/wing_e)+np.pi*ar*K*CDp)
        total_induced_drag = CDi_inv + K*CDp*(CL**2)
    else:
        total_induced_drag = CL **2 / (np.pi*ar*e)     
     
    conditions.aerodynamics.drag_breakdown.induced.total             = total_induced_drag
    conditions.aerodynamics.drag_breakdown.induced.efficiency_factor = wing_e 
    
    return total_induced_drag

 