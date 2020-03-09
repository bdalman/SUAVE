## @ingroup Analyses-Mission-Segments-Climb
# Constant_Stagnation_Pressure_Constant_Angle.py
#
# Created:  Apr 2019, B. Dalman
# Modified from original by: E. Botero 

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# SUAVE imports
from SUAVE.Methods.Missions import Segments as Methods
from SUAVE.Analyses.Mission.Segments import Conditions

from SUAVE.Analyses import Process

from .Unknown_Throttle import Unknown_Throttle

# Units
from SUAVE.Core import Units

# ----------------------------------------------------------------------
#  Segment
# ----------------------------------------------------------------------

## @ingroup Analyses-Mission-Segments-Climb
class Constant_Stagnation_Pressure_Constant_Angle(Unknown_Throttle):
    """ Climb at a constant dynamic pressure at a constant angle.
        This segment takes longer to solve than most because it has extra unknowns and residuals
    
        Assumptions:
        None
        
        Source:
        None
    """       
    
    def __defaults__(self):
        """ This sets the default solver flow. Anything in here can be modified after initializing a segment.
    
            Assumptions:
            None
    
            Source:
            N/A
    
            Inputs:
            None
    
            Outputs:
            None
    
            Properties Used:
            None
        """          
        
        # --------------------------------------------------------------
        #   User inputs
        # --------------------------------------------------------------
        self.altitude_start   = None # Optional
        self.altitude_end     = 10.  * Units.km
        self.climb_angle      = 3.   * Units.degrees
        self.stagnation_pressure = 101325 * Units.pascals
        
        # --------------------------------------------------------------
        #   State
        # --------------------------------------------------------------
        
        # conditions
        self.state.conditions.update( Conditions.Aerodynamics() )

        # initials and unknowns
        ones_row = self.state.ones_row        
        self.state.unknowns.throttle   = ones_row(1) * 0.5
        self.state.unknowns.body_angle = ones_row(1) * 3.0 * Units.deg
        self.state.unknowns.altitudes  = ones_row(1) * 0. * Units.km
        self.state.residuals.forces    = ones_row(3) * 0.0        
        
        # --------------------------------------------------------------
        #   The Solving Process
        # --------------------------------------------------------------
       

        initialize = self.process.initialize
        
        initialize.expand_state            = Methods.expand_state
        initialize.differentials           = Methods.Common.Numerics.initialize_differentials_dimensionless
        initialize.conditions              = Methods.Climb.Constant_Stagnation_Pressure_Constant_Angle.initialize_conditions_unpack_unknowns
        initialize.differentials_altitude  = Methods.Climb.Common.update_differentials_altitude
        
        # --------------------------------------------------------------
        #   Converge - starts iteration
        # --------------------------------------------------------------

        converge = self.process.converge

        converge.converge_root             = Methods.converge_root



        # --------------------------------------------------------------
        #   Iterate - this is iterated
        # --------------------------------------------------------------

        iterate = self.process.iterate
        

        # Update initials
        iterate.initials = Process()
        iterate.initials.time              = Methods.Common.Frames.initialize_time
        iterate.initials.weights           = Methods.Common.Weights.initialize_weights
        iterate.initials.inertial_position = Methods.Common.Frames.initialize_inertial_position
        iterate.initials.planet_position   = Methods.Common.Frames.initialize_planet_position



        # Unpack Unknowns
        iterate.unknowns = Process()
        iterate.unknowns.mission           = Methods.Climb.Constant_Stagnation_Pressure_Constant_Angle.initialize_conditions_unpack_unknowns
        
        
        # Update conditions
        iterate.conditions = Process()
        iterate.conditions.differentials   = Methods.Climb.Constant_Stagnation_Pressure_Constant_Angle.update_differentials
        iterate.conditions.acceleration    = Methods.Common.Frames.update_acceleration
        iterate.conditions.altitude        = Methods.Common.Aerodynamics.update_altitude
        iterate.conditions.atmosphere      = Methods.Common.Aerodynamics.update_atmosphere
        iterate.conditions.gravity         = Methods.Common.Weights.update_gravity
        iterate.conditions.freestream      = Methods.Common.Aerodynamics.update_freestream
        iterate.conditions.orientations    = Methods.Common.Frames.update_orientations
        iterate.conditions.aerodynamics    = Methods.Common.Aerodynamics.update_aerodynamics
        iterate.conditions.stability       = Methods.Common.Aerodynamics.update_stability
        iterate.conditions.propulsion      = Methods.Common.Energy.update_thrust
        iterate.conditions.weights         = Methods.Common.Weights.update_weights
        iterate.conditions.forces          = Methods.Common.Frames.update_forces
        iterate.conditions.planet_position = Methods.Common.Frames.update_planet_position
        
        # Solve Residuals
        iterate.residuals = Process()
        iterate.residuals.total_forces     = Methods.Climb.Constant_Stagnation_Pressure_Constant_Angle.residual_total_forces  


        # --------------------------------------------------------------
        #   Finalize - after iteration
        # --------------------------------------------------------------      
    
        finalize = self.process.finalize



        return
       