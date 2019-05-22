## @ingroup Analyses-Mission-Segments-Cruise
# Constant_Mach_Constant_Altitude_Vary_Dist.py
#
# Created:  Feb 2016, Andrew Wendorff
# Modified: Apr 2019, B. Dalman (Modified from Const_M_C_Alt)

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# SUAVE imports
from SUAVE.Methods.Missions import Segments as Methods

from .Constant_Speed_Constant_Altitude import Constant_Speed_Constant_Altitude

# Units
from SUAVE.Core import Units
from SUAVE.Analyses import Process

# ----------------------------------------------------------------------
#  Segment
# ----------------------------------------------------------------------

## @ingroup Analyses-Mission-Segments-Cruise
class Constant_Mach_Constant_Altitude_Vary_Dist(Constant_Speed_Constant_Altitude):
    """ Vehicle flies at a constant Mach number at a set altitude for a fixed distance
    
        Assumptions:
        Built off of a constant speed constant altitude segment
        
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
        self.altitude  = 3.0 * Units.km
        self.mach      = 0.5 
        self.target_landing_weight = 1000.0
        self.cruise_tag = 'cruise'
        self.distance  = 15. * Units.km


        # --------------------------------------------------------------
        # Unknowns
        # --------------------------------------------------------------

        # initials and unknowns
        ones_row = self.state.ones_row  
        self.state.unknowns.throttle = ones_row(1) * 0.5
        self.state.unknowns.body_angle = ones_row(1) * 3.0 * Units.deg
        self.state.unknowns.distance = ones_row(1) * 3.0 * Units.km

        self.state.residuals.forces = ones_row(3) * 0.
        self.state.residuals.landing_weight = ones_row(1) * 0

        
        # --------------------------------------------------------------
        #   The Solving Process
        # --------------------------------------------------------------
        initialize = self.process.initialize
        initialize.conditions = Methods.Cruise.Constant_Mach_Constant_Altitude_Vary_Dist.initialize_cruise_distance

        #print('First unknowns: ', self.state.unknowns)



        # --------------------------------------------------------------
        #   Converge
        # --------------------------------------------------------------
        self.process.converge.converge_root         = Methods.converge_root
        
        # --------------------------------------------------------------
        #   Iterate
        # --------------------------------------------------------------   
        '''
        iterate = self.process.iterate  
        #iterate.clear()
        
        # unpack the unknown
        iterate.unknowns = Process()
        iterate.unpack_distance              = Methods.Cruise.Constant_Mach_Constant_Altitude_Vary_Dist.unknown_cruise_distance
        
        # Run the Segments
        iterate.unpack                       = Methods.Common.Sub_Segments.unpack_subsegments
        iterate.sub_segments                 = Methods.Common.Sub_Segments.update_sub_segments
        iterate.merge_sub_segment_states     = Methods.Common.Sub_Segments.merge_sub_segment_states
        
        # Solve Residuals
        self.process.iterate.residual_weight = Methods.Cruise.Constant_Mach_Constant_Altitude_Vary_Dist.residual_landing_weight
        
        
        # --------------------------------------------------------------
        #   Finalize
        # --------------------------------------------------------------        
        self.process.finalize.sub_segments          = Methods.Common.Sub_Segments.finalize_sub_segments



        # ######################################################################################
        '''
        iterate = self.process.iterate
                
        # Update Initials
        iterate.initials = Process()
        iterate.initials.time              = Methods.Common.Frames.initialize_time
        iterate.initials.weights           = Methods.Common.Weights.initialize_weights
        iterate.initials.inertial_position = Methods.Common.Frames.initialize_inertial_position
        iterate.initials.planet_position   = Methods.Common.Frames.initialize_planet_position
        #iterate.unpack_distance            = Methods.Cruise.Constant_Mach_Constant_Altitude_Vary_Dist.unknown_cruise_distance
        
        # Unpack Unknowns
        iterate.unknowns = Process()
        iterate.unknowns.mission           = Methods.Cruise.Common.unpack_unknowns
        iterate.unknowns.unpack_distance   = Methods.Cruise.Constant_Mach_Constant_Altitude_Vary_Dist.unknown_cruise_distance

        #print('Printing unknowns: ', self.state.unknowns)
        
        # Update Conditions
        iterate.conditions = Process()
        #iterate.conditions.differentials   = Methods.Common.Numerics.update_differentials_time
        iterate.conditions.differentials   = Methods.Cruise.Constant_Mach_Constant_Altitude_Vary_Dist.update_differentials
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
        iterate.residuals.total_forces     = Methods.Cruise.Common.residual_total_forces
        iterate.residuals.residual_weight = Methods.Cruise.Constant_Mach_Constant_Altitude_Vary_Dist.residual_landing_weight

        
        # --------------------------------------------------------------
        #   Finalize - after iteration
        # --------------------------------------------------------------
        finalize = self.process.finalize
        
        # Post Processing
        #finalize.post_process = Process()        
        #finalize.post_process.inertial_position = Methods.Common.Frames.integrate_inertial_horizontal_position
        #finalize.post_process.stability         = Methods.Common.Aerodynamics.update_stability


        return

