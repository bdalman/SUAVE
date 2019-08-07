## @ingroup Analyses-Aerodynamics
# OpenVSP_surrogate.py
# 
# Created:   June 2019, B. Dalman


# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

import SUAVE
from SUAVE.Core import Data
from .Markup import Markup
from SUAVE.Analyses import Process

from .Vortex_Lattice import Vortex_Lattice
from .Process_Geometry import Process_Geometry
from SUAVE.Methods.Aerodynamics import Supersonic_Zero as Methods
from SUAVE.Methods.Aerodynamics import OpenVSP_Wave_Drag as VSP_Methods
from SUAVE.Methods.Aerodynamics.Common import Fidelity_Zero as Common
#from SUAVE.Methods.Aerodynamics.Surogate_Models import OpenVSP_surrogate
from .OpenVSP_Surrogate_Class import OpenVSP_Surrogate_Class

import numpy as np

# ----------------------------------------------------------------------
#  Class
# ----------------------------------------------------------------------
## @ingroup Analyses-Aerodynamics
class OpenVSP_Surrogate(Markup):
    """This is an analysis based on low-fidelity models.

    Assumptions:
    None

    Source:
    Many methods based on adg.stanford.edu, see methods for details
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
        self.tag = 'OpenVSP_Surrogate'
        
        # correction factors
        settings =  self.settings
        settings.fuselage_lift_correction           = 1.14
        settings.trim_drag_correction_factor        = 1.00      #Trim correction changed from 1.02 to 1.00 for small delta wing
        settings.wing_parasite_drag_form_factor     = 1.1
        settings.fuselage_parasite_drag_form_factor = 2.3       #Very small change in fuse para drag
        settings.aircraft_span_efficiency_factor    = 0.78      #Seems to not effect supersonic missions
        settings.viscous_lift_dependent_drag_factor = 0.38      #Also doesn't effect supersonic, but small effect on subsonic induced drag
        settings.drag_coefficient_increment         = 0.0000
        settings.oswald_efficiency_factor           = None
        settings.spoiler_drag_increment             = 0.00      #Line added to calc spoiler drag
        settings.maximum_lift_coefficient           = np.inf
        #settings.number_slices                      = 20
        #settings.number_rotations                   = 30
        
        # vortex lattice configurations
        #settings.number_panels_spanwise = 10
        #settings.number_panels_chordwise = 8
        
        
        # build the evaluation process
        compute = self.process.compute
        
        compute.lift = Process()
        #compute.lift.inviscid_wings                = Vortex_Lattice()
        #compute.lift.inviscid                      = OpenVSP_Surrogate.compute_lift   #Write this function
        compute.lift.inviscid                      = OpenVSP_Surrogate_Class()
        #compute.lift.vortex                        = Methods.Lift.vortex_lift #Vortex lift off because it wants to separately account for CL
        #compute.lift.compressible_wings            = Methods.Lift.wing_compressibility
        #compute.lift.fuselage                      = Common.Lift.fuselage_correction
        compute.lift.total                         = Common.Lift.aircraft_total
        
        compute.drag = Process()
        #compute.drag.compressibility               = Process()
        #compute.drag.compressibility.total         = VSP_Methods.compressibility_drag_total       

        #compute.drag.parasite                      = Process()

        #compute.drag.parasite.wings                = Process_Geometry('wings')
        #compute.drag.parasite.wings.wing           = Common.Drag.parasite_drag_wing 
        #compute.drag.parasite.fuselages            = Process_Geometry('fuselages')
        #compute.drag.parasite.fuselages.fuselage   = Common.Drag.parasite_drag_fuselage
        print('Warning: Propulsor parasite drag turned off in Analyses_Supersonic_OpenVSP_Wave_Drag')
        #compute.drag.parasite.propulsors           = Process_Geometry('propulsors')
        #compute.drag.parasite.propulsors.propulsor = Methods.Drag.parasite_drag_propulsor
        #compute.drag.parasite.pylons               = Methods.Drag.parasite_drag_pylon # supersonic pylon methods not currently available

        #compute.drag.parasite.total                = OpenVSP_surrogate.compute_drag
        #compute.drag.induced                       = Methods.Drag.induced_drag_aircraft
        #compute.drag.miscellaneous                 = Methods.Drag.miscellaneous_drag_aircraft
        #compute.drag.untrimmed                     = Common.Drag.untrimmed
        compute.drag.untrimmed                     = OpenVSP_Surrogate_Class()
        compute.drag.trim                          = Common.Drag.trim
        compute.drag.spoiler                       = Common.Drag.spoiler_drag    #Line added to calc spoiler drag
        compute.drag.total                         = Common.Drag.total_aircraft
        
        
    def initialize(self):
        """Initializes the surrogate needed for lift calculation and removes old volume drag data files.

        Assumptions:
        None

        Source:
        N/A

        Inputs:
        None

        Outputs:
        None

        Properties Used:
        self.geometry.tag (geometry in full is also attached to a process)
        """          
        import os
        
        # Remove old volume drag data so that new data can be appended without issues
        try:
            os.remove('volume_drag_data_' + self.geometry.tag + '.npy')  
        except:
            pass
        
        self.process.compute.lift.inviscid.geometry = self.geometry
        self.process.compute.lift.inviscid.initialize()

        self.process.compute.drag.untrimmed.geometry = self.geometry
        self.process.compute.drag.untrimmed.initialize()
        
    finalize = initialize        