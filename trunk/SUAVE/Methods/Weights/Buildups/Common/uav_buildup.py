## @ingroup Methods-Weights-Buildups-Common

# wing.py
#
# Created: Jun, 2017, J. Smart
# Modified: Apr, 2018, J. Smart

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------

from SUAVE.Core import Units
from SUAVE.Attributes.Solids import (
 Paint, Aluminum)


#-------------------------------------------------------------------------------
# Wing
#-------------------------------------------------------------------------------

## @ingroup Methods-Weights-Buildups-Common
def uav_buildup(vehicle,
         max_thrust, max_speed):
    
    """weight = SUAVE.Methods.Weights.Buildups.Common.wing(
            wing,
            config,
            maxThrust,
            numAnalysisPoints,
            safety_factor,
            max_g_load,
            moment_to_lift_ratio,
            lift_to_drag_ratio,
            forward_web_locations = [0.25, 0.35],
            rear_web_locations = [0.65, 0.75],
            shear_center = 0.25,
            margin_factor = 1.2)

        Calculates the structural mass of a wing for an eVTOL vehicle based on
        assumption of NACA airfoil wing, an assumed L/D, cm/cl, and structural
        geometry.

        Intended for use with the following SUAVE vehicle types, but may be used
        elsewhere:

            Electric Helicopter
            Electric Tiltrotor
            Electric Stopped Rotor

        Originally written as part of an AA 290 project intended for trade study
        of the above vehicle types plus an electricHelicopter.
        
        Sources:
        Project Vahana Conceptual Trade Study

        Inputs:

            wing                    SUAVE Wing Data Structure
            config                  SUAVE Confiug Data Structure
            maxThrust               Maximum Thrust                      [N]
            numAnalysisPoints       Analysis Points for Sizing          [Unitless]
            safety_factor           Design Saftey Factor                [Unitless]
            max_g_load              Maximum Accelerative Load           [Unitless]
            moment_to_lift_ratio    Coeff. of Moment to Coeff. of Lift  [Unitless]
            lift_to_drag_ratio      Coeff. of Lift to Coeff. of Drag    [Unitess]
            forward_web_locations   Location of Forward Spar Webbing    [m]
            rear_web_locations      Location of Rear Spar Webbing       [m]
            shear_center            Location of Shear Center            [m]
            margin_factor           Allowable Extra Mass Fraction       [Unitless]

        Outputs:

            weight:                 Wing Mass                           [kg]
    """

#-------------------------------------------------------------------------------
# Unpack Inputs
#-------------------------------------------------------------------------------
    #print(vehicle.fuselages)

    MTOW                        = vehicle.mass_properties.max_takeoff
    
    wingArea                    = vehicle.wings['main_wing'].areas.wetted
    wingRefArea                 = vehicle.wings['main_wing'].areas.reference
    mach                        = max_speed
    wingAR                      = vehicle.wings['main_wing'].aspect_ratio
    fuelVolWing                 = vehicle.wings['main_wing'].fuel_volume
    fuelVolFuse                 = vehicle.fuselages['fuselage'].fuel_volume
    try:                    #This block currently only catches one specific exception. Should re-write to be general
        tailArea                = vehicle.wings['vertical_stabilizer'].areas.wetted
    except:
        tailArea                = vehicle.wings['v_tail'].areas.wetted


    fuelVol                     = fuelVolWing + fuelVolFuse



    #print('Fuel Vol Updated: ', fuelVol, fuelVolFuse, fuelVolWing)

    fuseArea                    = vehicle.fuselages['fuselage'].areas.wetted
    thrust                      = max_thrust


    totalArea                   = wingArea + tailArea + fuseArea

    #print('Printing mass stuff: ', wingArea, tailArea, fuseArea, fuelVol)


#-------------------------------------------------------------------------------
# Unpack Material Properties
#-------------------------------------------------------------------------------
    
    ALUM = Aluminum()
    ALUM_DEN = ALUM.density
    ALUM_MGT = ALUM.minimum_gage_thickness
    ALUM_UTS = ALUM.ultimate_tensile_strength
    
    PAINT = Paint()
    PAINT_MGT = PAINT.minimum_gage_thickness
    PAINT_DEN = PAINT.density


    #---------------------------------------------------------------------------
    # Structural Calculations
    #---------------------------------------------------------------------------

    # Calculate Wing Weight Based on wetted area

    wing_weight = wingArea * ALUM_DEN * 0.0047625            # Assumes plates of 3/16" thickness. Should add in factor for spar or bulkheads
    #wing_weight = wingArea * 11.8689
    #wing_weight = wingArea * -21.8708

    # Calculate fuselage mass from wetted area. This also assumes aluminum plates, but isn't quite as realistic

    #fuse_weight = fuseArea * 0.003175 * ALUM_DEN          # Assumes plates of 1/8" thickness. How we make a fuse out of solid plates sounds like Will's problem not mine :)
    fuse_weight = fuseArea * 0.00635 * ALUM_DEN  
    #fuse_weight = fuseArea * -12.3299   
    #fuse_weight = fuseArea * 70.4091       

    # Vertical tail weight

    tail_weight = tailArea * 0.003175 * ALUM_DEN           # Assumes 1/8" again.
    #tail_weight = tailArea * 149.2303
    #tail_weight = tailArea * -90.5178

    # Propulsion weight. Based off turbojet table, and linear slope of thrust vs. weight.

    prop_weight = 0.014 * thrust - 1.2374               # [kg] Eqn from linear fit to turbojets. Thrust in N

    # Mass of the fuel (assuming kerosene), given all the wing space contains fuel

    fuel_weight = fuelVol * 810                            # [kg] Based on kerosene density in kg/m^3

    # Mass of the electronics


    # Other misc mass


    # Mass of available payload

    #W_af = 7.4955 * (totalArea**1.2707) * (mach * (1/0.98)**0.48)
    W_af = 5.907 * (totalArea**1.4907) * (mach)
    #W_af = 0.8247 * (totalArea**1.3756) * (mach**0.4721)

    #print('Weight params are: ', totalArea, mach, thrust, W_af, prop_weight)


    payload_weight = MTOW - (W_af + fuel_weight + prop_weight)

    #print('WARNING: Weight estimates are tripled to test L/D result!')
    # Now start to pack up properties
    '''
    vehicle.mass_properties.max_zero_fuel   = wing_weight + fuse_weight + tail_weight + prop_weight # Weight with everything except fuel
    vehicle.mass_properties.cargo           = payload_weight
    vehicle.mass_properties.takeoff         = wing_weight + fuse_weight + tail_weight + prop_weight + fuel_weight    # Weight without any payload
    vehicle.mass_properties.operating_empty = wing_weight + fuse_weight + tail_weight + prop_weight + 0.02*fuse_weight           # No payload, no fuel
    vehicle.mass_properties.wing_weight     = wing_weight
    vehicle.mass_properties.fuselage_weight = fuse_weight
    vehicle.mass_properties.tail_weight     = tail_weight
    vehicle.mass_properties.propulsion_weight = prop_weight
    vehicle.mass_properties.fuel_weight     = fuel_weight
    '''

    vehicle.mass_properties.max_zero_fuel   = W_af + prop_weight # Weight with everything except fuel
    vehicle.mass_properties.cargo           = payload_weight
    vehicle.mass_properties.takeoff         = W_af + prop_weight + fuel_weight    # Weight without any payload
    vehicle.mass_properties.operating_empty = W_af + prop_weight + 0.02*0.4*W_af           # No payload, no fuel
    vehicle.mass_properties.wing_weight     = wing_weight
    vehicle.mass_properties.fuselage_weight = fuse_weight
    vehicle.mass_properties.tail_weight     = tail_weight
    vehicle.mass_properties.propulsion_weight = prop_weight
    vehicle.mass_properties.fuel_weight     = fuel_weight

    #print('Printing TOW: ', vehicle.mass_properties.takeoff, prop_weight, fuel_weight)

    return vehicle