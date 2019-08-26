## @ingroup Methods-Aerodynamics-Common-Fidelity_Zero-Drag
# untrimmed_SU2.py
#
# Created:  Jan 2014, T. Orra
# Modified: Jan 2016, E. Botero  

# ----------------------------------------------------------------------
#  Adds the parasite drag into the drag prediction given by the inviscid CFD method in SU2
# ----------------------------------------------------------------------

## @ingroup Methods-Aerodynamics-Common-Fidelity_Zero-Drag
def untrimmed_SU2(state,settings,geometry):
    """Sums aircraft drag before trim correction

    Assumptions:
    None

    Source:
    None

    Inputs:
    state.conditions.aerodynamics.drag_breakdown.
      parasite.total                              [Unitless]
      inviscid                                    [Unitless]
        -this should incorporate induced and wave drag. Misc drag is ignored for this

    Outputs:
    aircraft_untrimmed                            [Unitless]

    Properties Used:
    N/A
    """       

    # unpack inputs
    conditions     = state.conditions
    configuration  = settings
    drag_breakdown = conditions.aerodynamics.drag_breakdown

    # various drag components
    #print(conditions.aerodynamics.inviscid_drag_coefficient.keys())
    #print(conditions.aerodynamics.inviscid_drag_coefficient)
    #print(conditions.aerodynamics.drag_breakdown.untrimmed.keys())

    parasite_total        = conditions.aerodynamics.drag_breakdown.parasite.total            
    inviscid              = conditions.aerodynamics.inviscid_drag_coefficient           

    # untrimmed drag
    aircraft_untrimmed = parasite_total        \
                       + inviscid

    
    conditions.aerodynamics.drag_breakdown.untrimmed = aircraft_untrimmed
    
    return aircraft_untrimmed