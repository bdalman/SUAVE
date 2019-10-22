# segment_properties.py
#
# Created:  Apr 2019, T. MacDonald

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

import numpy as np
from SUAVE.Core import Data

# ----------------------------------------------------------------------
#  Methods
# ----------------------------------------------------------------------
def segment_properties(settings,wing):
    """Computes detailed segment properties. These are currently used for parasite drag calculations.

    Assumptions:
    Segments are trapezoids

    Source:
    http://aerodesign.stanford.edu/aircraftdesign/aircraftdesign.html (Stanford AA241 A/B Course Notes)

    Inputs:
    wing.
      exposed_root_chord_offset [m]
      symmetric                 [-]
      spans.projected           [m]
      thickness_to_chord        [-]
      areas.reference           [m^2]
      areas.wetted              [m^2]
      chords.root               [m]
      Segments.
        percent_span_location   [-]
        root_chord_percent      [-]

    Outputs:
    wing.areas.wetted           [m^2]
    wing.Segments.
      taper                     [-]
      chords.mean_aerodynamic   [m]
      areas.
        reference               [m^2]
        exposed                 [m^2]
        wetted                  [m^2]
        

    Properties Used:
    N/A
    """  
    
    C = settings.wing_parasite_drag_form_factor
    
    # Unpack wing
    exposed_root_chord_offset = wing.exposed_root_chord_offset
    symm                      = wing.symmetric
    semispan                  = wing.spans.projected*0.5 * (2 - symm)
    t_c_w                     = wing.thickness_to_chord
    Sref                      = wing.areas.reference
    num_segments              = len(wing.Segments.keys())      
    
    total_wetted_area            = 0  
    root_chord                   = wing.chords.root    
    
    for i_segs in range(num_segments):
        if i_segs == num_segments-1:
            continue 
        else:  
            span_seg  = semispan*(wing.Segments[i_segs+1].percent_span_location - wing.Segments[i_segs].percent_span_location ) 
            segment   = wing.Segments[i_segs]         
            
            if i_segs == 0:
                chord_root    = root_chord*wing.Segments[i_segs].root_chord_percent
                chord_tip     = root_chord*wing.Segments[i_segs+1].root_chord_percent   
                wing_root     = chord_root + exposed_root_chord_offset*((chord_tip - chord_root)/span_seg)

                taper         = chord_tip/wing_root  
                mac_seg       = wing_root  * 2/3 * (( 1 + taper  + taper**2 )/( 1 + taper))  
                Sref_seg      = span_seg*(chord_root+chord_tip)*0.5 
                S_exposed_seg = (span_seg-exposed_root_chord_offset)*(wing_root+chord_tip)*0.5                    
            
            else: 
                chord_root    = root_chord*wing.Segments[i_segs].root_chord_percent
                chord_tip     = root_chord*wing.Segments[i_segs+1].root_chord_percent
                taper         = chord_tip/chord_root   
                mac_seg       = chord_root * 2/3 * (( 1 + taper  + taper**2 )/( 1 + taper))
                Sref_seg      = span_seg*(chord_root+chord_tip)*0.5
                S_exposed_seg = Sref_seg

            if wing.symmetric:
                Sref_seg = Sref_seg*2
                S_exposed_seg = S_exposed_seg*2
            
            # compute wetted area of segment
            if t_c_w < 0.05:
                Swet_seg = 2.003* S_exposed_seg
            else:
                Swet_seg = (1.977 + 0.52*t_c_w) * S_exposed_seg
                
            segment.taper                   = taper
            segment.chords                  = Data()
            segment.chords.mean_aerodynamic = mac_seg
            segment.areas.reference         = Sref_seg
            segment.areas.exposed           = S_exposed_seg
            segment.areas.wetted            = Swet_seg
            
            total_wetted_area += Swet_seg
            
    wing.areas.wetted = total_wetted_area 
        
    return