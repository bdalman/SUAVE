# wing_planform.py
#
# Created:  Apr 2014, T. Orra
# Modified: Jan 2016, E. Botero

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

import numpy as np
from SUAVE.Core import Data

# ----------------------------------------------------------------------
#  Methods
# ----------------------------------------------------------------------
def wing_planform_sections(wing):
    """Computes the dimensions of a multisectioned wing, with an arbitrary number of sections

    Assumptions:
    Trapezoidal wing sections with no leading/trailing edge extensions
    Required wing parameters are defined for each wing section
    ***Does not account for high lift devices

    Source:
    None

    Inputs:
    wing.
      spans.projected          [m^2]
      root_chord               [m]
      thickness_to_chord       [-]
      dihedral                 [radians]
      vertical                 <boolean> Determines if wing is vertical
      symmetric                <boolean> Determines if wing is symmetric
      origin                   [m]       x, y, and z position
      segments.
        span percents
        segment_twists
        segment_root_chord percents
        segment_dihedrals
        segment_le_sweeps


    Outputs:
    wing.
      chords.root              [m]
      chords.tip               [m]
      chords.mean_aerodynamics [m]
      areas.wetted             [m^2]
      areas.affected           [m^2]
      spans.projected          [m]
      aerodynamic_center       [m]      x, y, and z location
      leading edge sweep
      e (span efficiency from raymer)
      wing total length (tip to tip, similar to span)


    Properties Used:
    N/A
    """      

    num_sections = len(wing.Segments)
    num_sec_less_one = num_sections -1

    
    # unpack high level settings
    span        = wing.spans.projected
    taper       = wing.taper                           #Uses wing.taper to set tip chord based on previous section chord
    chord_root  = wing.root_chord                       #New
    #sweep       = wing.sweeps.leading_edge             # Remove??
    #ar          = wing.aspect_ratio                    #Remove input??
    t_c_w       = wing.thickness_to_chord
    dihedral    = wing.dihedral 
    vertical    = wing.vertical
    symmetric   = wing.symmetric
    origin_x, origin_y, origin_z      = wing.origin


    # Initialize segment level settings
    span_percents           = np.zeros(num_sections, dtype=float)
    segment_twist           = np.zeros(num_sections, dtype=float)
    segment_root_chord_per  = np.zeros(num_sections, dtype=float)
    segment_chord           = np.zeros(num_sections, dtype=float)
    segment_dihedrals       = np.zeros(num_sections, dtype=float)
    segment_le_sweeps       = np.zeros(num_sections, dtype=float)
    segment_thickness       = np.zeros(num_sections, dtype=float)
    segment_taper           = np.zeros(num_sections, dtype=float)

    segment_ar              = np.zeros(num_sections, dtype=float)
    segment_area            = np.zeros(num_sections, dtype=float)
    sweep_dist              = np.zeros(num_sections-1, dtype=float)
    segment_HC_sweep        = np.zeros(num_sections, dtype=float)
    segment_length          = np.zeros(num_sections-1, dtype=float)
    wing_segment_x_cg       = np.zeros(num_sections-1, dtype=float)


    #Setting the initial values for computation
    segment_chord[0] = chord_root

    # Unpack segment level settings
    for i in range(0, num_sections):
        segment_root_chord_per[i]   = wing.Segments[i].root_chord_percent
        span_percents[i]            = wing.Segments[i].percent_span_location
        segment_twist[i]            = wing.Segments[i].twist
        
        segment_dihedrals[i]        = wing.Segments[i].dihedral_outboard
        segment_le_sweeps[i]        = wing.Segments[i].sweeps.leading_edge
        segment_thickness[i]        = wing.Segments[i].thickness_to_chord

    #Set tip chord based off taper and previous section chord
    segment_root_chord_per[-1] = segment_root_chord_per[-2] * chord_root * taper

    for j in range(0, num_sections):              #Separate loop because root chord percent needs to be filled already
        if j != (num_sections-1):
            segment_taper[j] = segment_root_chord_per[j+1]/segment_root_chord_per[j]                 #New



    for ii in range(0, num_sec_less_one):
        segment_chord[ii+1]      = segment_chord[ii] * segment_taper[ii]                                                              # Calculate tip chord based off section taper and previous root chord
        segment_area[ii]         = (segment_chord[ii]+segment_chord[ii+1])*0.5 * (span_percents[ii+1]-span_percents[ii])*(span)      #Calculate section area. THIS ASSUMES SYMMETRIC WINGS
        segment_ar[ii]           = ((span_percents[ii+1]-span_percents[ii])*span)**2/segment_area[ii]
        segment_HC_sweep[ii]         = np.arctan(np.tan(segment_le_sweeps[ii]) - (4./segment_ar[ii])*(0.5-0.)*(1.-segment_taper[ii])/(1.+segment_taper[ii]))



    #print('Printing result vectors: ', segment_taper, segment_ar, segment_le_sweeps, segment_HC_sweep)
    #print("Span percents are:", span_percents)


    # calculate some high-level parameters


    sref       = np.sum(segment_area)           #Total wing planform
    ar         = span**2/sref                   #Total wing aspect ratio

    # Calculating thickness + dihedral won't be done here, just assuming they are constant for each section. Could write a loop to do an area weighted average if required.
    t_c_w = wing.Segments[0].thickness_to_chord
    dihedral = wing.Segments[0].dihedral_outboard
    # Other key parameters:
    taper = segment_chord[-1]/segment_chord[0]
    chord_tip = segment_chord[-1]

    #Calculate LE sweep from first to 
    for i in range(0, num_sec_less_one):
        sweep_dist[i]       = np.tan(segment_le_sweeps[i])*(span_percents[i+1]-span_percents[i])*(span/2)
        segment_length[i]   = (span*0.5)*(span_percents[i+1]-span_percents[i])/np.cos(segment_HC_sweep[i])

    total_sweep_dist = np.sum(sweep_dist)

    le_sweep = np.arctan(total_sweep_dist/(span*0.5))

    
    swet = 2.*span/2.*(chord_root+chord_tip) *  (1.0 + 0.2*t_c_w)

    mac = 2./3.*( chord_root+chord_tip - chord_root*chord_tip/(chord_root+chord_tip) )

    total_length = np.sum(segment_length) * 2

    # span efficency
    e = 4.61 * (1-0.045 * ar**0.68)*np.cos(le_sweep)**0.15 -3.1  #Method from Raymer. Not valid for sweep < 30deg

    # estimating aerodynamic center coordinates
    y_coord = span / 6. * (( 1. + 2. * taper ) / (1. + taper))
    x_coord = mac * 0.25 + y_coord * np.tan(le_sweep) #+ origin_x
    z_coord = y_coord * np.tan(dihedral)

    if vertical:
        temp    = y_coord * 1.
        y_coord = z_coord * 1.
        z_coord = temp

    if symmetric:
        y_coord = 0 

    affected_area = 0   # To do with flaps   


    #Now calculate CG, making the assumption that weight is directly proportional to area
    for jj in range(0, num_sec_less_one):
        wing_segment_x_cg[jj] = (segment_chord[jj]+segment_chord[jj+1])*0.5 + sweep_dist[jj]*0.5
        #For now we don't care about y or z, since we assume the wing is symmetrical, and no dihedral

    placeholder_2 = 0
    for ii in range(0, num_sec_less_one):
        placeholder_2 = placeholder_2 + wing_segment_x_cg[ii]*segment_area[ii]

    wing_x_cg = placeholder_2 / sref

    if segment_le_sweeps[0] < 0.9599: # If first segment sweep is less than 55deg use total wing sweep. Else, use first segment since it should get you out of the mach cone
        le_sweep = np.arctan(total_sweep_dist/(span*0.5))   #Uses half span because we're using only one triangle
    else:
        le_sweep = segment_le_sweeps[0]

        
    # update/repack
    wing.chords.root                = chord_root
    wing.chords.tip                 = chord_tip
    wing.chords.mean_aerodynamic    = mac
    wing.areas.wetted               = swet
    wing.areas.affected             = affected_area
    wing.areas.reference            = sref
    wing.aspect_ratio               = ar
    wing.aerodynamic_center         = [x_coord , y_coord, z_coord]
    wing.mass_properties            = Data()
    wing.mass_properties.center_of_gravity = [wing_x_cg, 0, 0 ]
    wing.origin                     = [origin_x, origin_y, origin_z]
    wing.sweeps.leading_edge        = le_sweep                              #For drag purposes should I be using average (as currently set), or interior??)
    wing.span_efficiency            = e
    wing.total_length               = total_length
    for ii in range(0, num_sections):
        wing.Segments[ii].areas.reference = segment_area[ii]
        wing.Segments[ii].aspect_ratio = segment_ar[ii]
        wing.Segments[ii].taper         = segment_taper[ii]

    #Need to add wing CG estimate
    
    return wing