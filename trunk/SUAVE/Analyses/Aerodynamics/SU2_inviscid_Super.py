## @ingroup Analyses-Aerodynamics
# SU2_inviscid.py
#
# Created:  Sep 2016, E. Botero
# Modified: Jan 2017, T. MacDonald
# Modified: May 2020, B. Dalman

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# SUAVE imports
import SUAVE
from SUAVE.Core import Data, Units

# Local imports
from .Aerodynamics import Aerodynamics
from SUAVE.Input_Output.SU2.call_SU2_CFD import call_SU2_CFD
from SUAVE.Input_Output.SU2.write_SU2_cfg import write_SU2_cfg

# Package imports
import numpy as np
import time
import pylab as plt
import sklearn
from sklearn import gaussian_process
from sklearn import neighbors
from sklearn import svm

from sklearn.gaussian_process.kernels import ExpSineSquared

from SUAVE.Methods.Aerodynamics.Supersonic_Zero.Drag.Cubic_Spline_Blender import Cubic_Spline_Blender
from scipy.interpolate import RectBivariateSpline, RegularGridInterpolator


# ----------------------------------------------------------------------
#  Class
# ----------------------------------------------------------------------
## @ingroup Analyses-Aerodynamics
class SU2_inviscid_Super(Aerodynamics):
    """This builds a surrogate and computes lift and drag using SU2

    Assumptions:
    Inviscid

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
        self.tag = 'SU2_inviscid'

        self.geometry = Data()
        self.settings = Data()
        self.settings.half_mesh_flag     = True
        self.settings.parallel           = False
        self.settings.processors         = 1
        self.settings.maximum_iterations = 1500
        self.settings.CFD_failed_flag    = False
        self.settings.plot_surrogate_flag = True
        self.settings.physical_problem   = 'EULER'

        # Conditions table, used for surrogate model training
        self.training = Data()        
        self.training.angle_of_attack  = np.array([-2.,3.,8.]) * Units.deg
        self.training.Mach             = np.array([0.3,0.7,0.85, 1.1])
        self.training.lift_coefficient = None
        self.training.drag_coefficient = None
        self.training_file             = None

        # blending function 
        self.hsub_min                                = 0.85
        self.hsub_max                                = 0.95
        self.hsup_min                                = 1.05
        self.hsup_max                                = 1.25 
        
        # Surrogate model
        self.surrogates = Data()

        # Storage for passing things out that aren't explicitely lift or drag
        self.storage   = Data()
 
        
    def initialize(self):
        """Drives functions to get training samples and build a surrogate.

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
        # Sample training data
        self.sample_training()
        
        self.build_surrogate()

        plot_surrogate = self.settings.plot_surrogate_flag

        if plot_surrogate:
            self.plot_surrogate()
            self.settings.plot_surrogate_flag = False


    def evaluate(self,state,settings,geometry):
        """Evaluates lift and drag using available surrogates.

        Assumptions:
        None

        Source:
        N/A

        Inputs:
        state.conditions.
          mach_number      [-]
          angle_of_attack  [radians]

        Outputs:
        inviscid_lift      [-] CL
        inviscid_drag      [-] CD

        Properties Used:
        self.surrogates.
          lift_coefficient [-] CL
          drag_coefficient [-] CD
        """ 
        # Unpack
        if self.settings.CFD_failed_flag == True: #Already have flag set, so just send back reasonable values so it can still converge
            inviscid_lift = 1.0
            inviscid_drag = 0.2
            return inviscid_lift, inviscid_drag

        surrogates = self.surrogates        
        conditions = state.conditions
        x_ac       = self.storage.aerodynamic_center

        hsub_min   = self.hsub_min
        hsub_max   = self.hsub_max
        hsup_min   = self.hsup_min
        hsup_max   = self.hsup_max

        # Spline for Subsonic-to-Transonic-to-Supesonic Regimes
        sub_trans_spline = Cubic_Spline_Blender(hsub_min,hsub_max)
        h_sub            = lambda M:sub_trans_spline.compute(M)          
        sup_trans_spline = Cubic_Spline_Blender(hsup_min,hsup_max) 
        h_sup            = lambda M:sup_trans_spline.compute(M) 

        print('Turn on line 175 and 211 in SU2_invisc_super when modelling fuse again for CM calc!')
        #vehicle_length = geometry.fuselages['fuselage'].lengths.total        
        mach = conditions.freestream.mach_number
        AoA  = conditions.aerodynamics.angle_of_attack
        # Unapck the surrogates
        CL_surrogate_sub          = surrogates.lift_coefficient_subsonic  
        CL_surrogate_sup          = surrogates.lift_coefficient_supersonic  
        CL_surrogate_trans        = surrogates.lift_coefficient_transonic
        CDinvisc_surrogate_sub         = surrogates.drag_coefficient_subsonic  
        CDinvisc_surrogate_sup         = surrogates.drag_coefficient_supersonic  
        CDinvisc_surrogate_trans       = surrogates.drag_coefficient_transonic


        # Inviscid lift
        data_len = len(AoA)
        inviscid_lift = np.zeros([data_len,1])
        for ii,_ in enumerate(AoA):
            inviscid_lift[ii] = h_sub(mach[ii])*CL_surrogate_sub(AoA[ii],mach[ii],grid=False)    +\
                          (h_sup(mach[ii]) - h_sub(mach[ii]))*CL_surrogate_trans((AoA[ii],mach[ii]))+ \
                          (1- h_sup(mach[ii]))*CL_surrogate_sup(AoA[ii],mach[ii],grid=False)

        conditions.aerodynamics.lift_breakdown.inviscid_wings_lift       = Data()
        conditions.aerodynamics.lift_breakdown.inviscid_wings_lift.total = inviscid_lift
        conditions.aerodynamics.lift_breakdown.inviscid_wings_lift.main_wing = inviscid_lift
        state.conditions.aerodynamics.lift_coefficient                   = inviscid_lift
        state.conditions.aerodynamics.lift_breakdown.compressible_wings  = inviscid_lift
        
        # Inviscid drag, zeros are a placeholder for possible future implementation
        inviscid_drag = np.zeros([data_len,1])
        for ii,_ in enumerate(AoA):
            inviscid_drag[ii] = h_sub(mach[ii])*CDinvisc_surrogate_sub(AoA[ii],mach[ii],grid=False)    +\
                          (h_sup(mach[ii]) - h_sub(mach[ii]))*CDinvisc_surrogate_trans((AoA[ii],mach[ii]))+ \
                          (1- h_sup(mach[ii]))*CDinvisc_surrogate_sup(AoA[ii],mach[ii],grid=False)
      
        state.conditions.aerodynamics.inviscid_drag_coefficient    = inviscid_drag
        state.conditions.aerodynamics.drag_breakdown.untrimmed     = inviscid_drag
        
        #geometry.aerodynamic_center = x_ac * vehicle_length

        return inviscid_lift, inviscid_drag


    def sample_training(self):
        """Call methods to run SU2 for sample point evaluation.

        Assumptions:
        None

        Source:
        N/A

        Inputs:
        see properties used

        Outputs:
        self.training.
          coefficients     [-] CL and CD
          grid_points      [radians,-] angles of attack and mach numbers 

        Properties Used:
        self.geometry.tag  <string>
        self.training.     
          angle_of_attack  [radians]
          Mach             [-]
        self.training_file (optional - file containing previous AVL data)
        """                
        # Unpack
        geometry = self.geometry
        settings = self.settings
        training = self.training
        
        AoA  = training.angle_of_attack
        mach = training.Mach 
        CL   = np.zeros([len(AoA)*len(mach),1])
        CD   = np.zeros([len(AoA)*len(mach),1])
        CM   = np.zeros([len(AoA)*len(mach),1])

        # Condition input, local, do not keep (k is used to avoid confusion)
        konditions              = Data()
        konditions.aerodynamics = Data()

        if self.training_file is None:
            # Calculate aerodynamics for table
            table_size = len(AoA)*len(mach)
            xy = np.zeros([table_size,2])
            count = 0
            time0 = time.time()
            for i,_ in enumerate(AoA):
                for j,_ in enumerate(mach):
                    
                    xy[count,:] = np.array([AoA[i],mach[j]])
                    # Set training conditions
                    konditions.aerodynamics.angle_of_attack = AoA[i]
                    konditions.aerodynamics.mach            = mach[j]
                    
                    CL[count],CD[count], CM[count] = call_SU2(konditions, settings, geometry)
                    count += 1
            
            time1 = time.time()
            
            print('The total elapsed time to run SU2: '+ str(time1-time0) + '  Seconds')
            time_elapsed = time1-time0

            if max(CD) > 9000 or time_elapsed < 15: #Saw one instance take 12s for 12 different runs
                self.settings.CFD_failed_flag = True
            else:
                self.settings.CFD_failed_flag = False
        else:
            data_array = np.loadtxt(self.training_file)
            xy         = data_array[:,0:2]
            CL         = data_array[:,2:3]
            CD         = data_array[:,3:4]
            CM         = data_array[:,4:5]

            # Now we need to set the training Mach and AOA to be whatever were in this file, otherwise it'll get confused and could build the surrogate on incorrect values

            AoA_array = xy[:,0]
            Mach_array = xy[:,1]

            for i in range(0,len(AoA_array)):
                if AoA_array[i] != AoA_array[0]:
                    mach_split = i
                    break

            AoA_matrix = np.reshape(AoA_array, (int(len(AoA_array)/mach_split), mach_split) )
            Mach_matrix = np.reshape(Mach_array, (int(len(Mach_array)/mach_split), mach_split))

            AoA_train = AoA_matrix[:,0]
            Mach_train = Mach_matrix[0,:]

            training.angle_of_attack = AoA_train
            training.Mach            = Mach_train


        # Save the data
        np.savetxt(geometry.tag+'_data.txt',np.hstack([xy,CL,CD,CM]),fmt='%10.8f',header='AoA Mach CL CD CM')

        print('Added location of training_file to aerodynamics data structure after creation!')
        self.training_file = geometry.tag+'_data.txt'

        # Store training data
        training.coefficients = np.hstack([CL,CD, CM])
        training.grid_points  = xy

        return

    def build_surrogate(self):
        """Builds a surrogate based on sample evalations using a 2nd (and in some cases 1st) order RectBivariateSpline (no longer uses Gaussian process).

        Assumptions:
        None

        Source:
        N/A

        Inputs:
        self.training.
          coefficients     [-] CL and CD
          grid_points      [radians,-] angles of attack and mach numbers 

        Outputs:
        self.surrogates.
          lift_coefficient <Guassian process surrogate>
          drag_coefficient <Guassian process surrogate>

        Properties Used:
        No others
        """  
        # Unpack data
        training  = self.training
        AoA_data  = training.angle_of_attack
        mach_data = training.Mach
        CL_data   = training.coefficients[:,0]
        CD_data   = training.coefficients[:,1]
        CM_data   = training.coefficients[:,2]
        xy        = training.grid_points # [AOA, Mach]
        
        #import pyKriging
        
        # Gaussian Process New
        #regr_cl_sup = gaussian_process.GaussianProcess()
        #regr_cl_sub = gaussian_process.GaussianProcess()

        # gp_kernel_ES = ExpSineSquared(length_scale=1.0, periodicity=1.0, length_scale_bounds=(1e-5,1e5), periodicity_bounds=(1e-5,1e5))

        # regr_cl_sup = gaussian_process.GaussianProcessRegressor(kernel=gp_kernel_ES)
        # regr_cl_sub = gaussian_process.GaussianProcessRegressor(kernel=gp_kernel_ES)
        # regr_cd_sup = gaussian_process.GaussianProcessRegressor(kernel=gp_kernel_ES)
        # regr_cd_sub = gaussian_process.GaussianProcessRegressor(kernel=gp_kernel_ES)

        # cl_surrogate_sup = regr_cl_sup.fit(xy[xy[:,1]>=1.], CL_data[xy[:,1]>=1.])
        # cl_surrogate_sub = regr_cl_sub.fit(xy[xy[:,1]<=1.], CL_data[xy[:,1]<=1.])
        # cd_surrogate_sup = regr_cd_sup.fit(xy[xy[:,1]>=1.], CD_data[xy[:,1]>=1.])
        # cd_surrogate_sub = regr_cd_sub.fit(xy[xy[:,1]<=1.], CD_data[xy[:,1]<=1.])  
        #regr_cd = gaussian_process.GaussianProcess()
        #regr_cd = gaussian_process.GaussianProcessRegressor(kernel=gp_kernel_ES)
        #cd_surrogate = regr_cd.fit(xy, CD_data)        
        
        # Gaussian Process New
        #regr_cl = gaussian_process.GaussianProcessRegressor()
        #regr_cd = gaussian_process.GaussianProcessRegressor()
        #cl_surrogate = regr_cl.fit(xy, CL_data)
        #cd_surrogate = regr_cd.fit(xy, CD_data)  
        
        # KNN
        #regr_cl = neighbors.KNeighborsRegressor(n_neighbors=1,weights='distance')
        #regr_cd = neighbors.KNeighborsRegressor(n_neighbors=1,weights='distance')
        #cl_surrogate = regr_cl.fit(xy, CL_data)
        #cd_surrogate = regr_cd.fit(xy, CD_data)  
        
        # SVR
        #regr_cl = svm.SVR(C=500.)
        #regr_cd = svm.SVR()
        #cl_surrogate = regr_cl.fit(xy, CL_data)
        #cd_surrogate = regr_cd.fit(xy, CD_data)

        #### New Surrogate creation - based off Vortex_Lattice.py surrogate

        #Start by splitting Mach and L/D into sub/sup
        mach_data_sub = mach_data[mach_data < 1]
        mach_data_sup = mach_data[mach_data >= 1]

        CL_data_sub_hold = CL_data[xy[:,1] < 1]
        CL_data_sup_hold = CL_data[xy[:,1] >= 1]
        CDinviscnvisc_data_sub_hold = CD_data[xy[:,1] < 1]
        CDinviscnvisc_data_sup_hold = CD_data[xy[:,1] >= 1]

        CL_data_sub = np.reshape(CL_data_sub_hold, (len(AoA_data), int(len(CL_data_sub_hold)/len(AoA_data)) ) )
        CL_data_sup = np.reshape(CL_data_sup_hold, (len(AoA_data), int(len(CL_data_sup_hold)/len(AoA_data)) ) )
        CDinviscnvisc_data_sub = np.reshape(CDinviscnvisc_data_sub_hold, (len(AoA_data), int(len(CDinviscnvisc_data_sub_hold)/len(AoA_data))))
        CDinviscnvisc_data_sup = np.reshape(CDinviscnvisc_data_sup_hold, (len(AoA_data), int(len(CDinviscnvisc_data_sup_hold)/len(AoA_data))))

        # print(CL_data_sub)
        # print(CL_data_sup)
        # print(AoA_data)
        #print(mach_data_sub)


        lenAoA, lenMachSup = CL_data_sup.shape

        # Now split out transonic section

        CL_data_trans        = np.zeros((len(AoA_data),2))       
        CDinviscnvisc_data_trans       = np.zeros((len(AoA_data),2)) 
        CL_data_trans[:,0]   = CL_data_sub[:,-1]
        CL_data_trans[:,1]   = CL_data_sup[:, 0]
        #CL_data_trans[:,2]   = CL_data_sup[:, 1]
        CDinviscnvisc_data_trans[:,0]  = CDinviscnvisc_data_sub[:,-1]
        CDinviscnvisc_data_trans[:,1]  = CDinviscnvisc_data_sup[:,0]

        mach_data_trans_CL   = np.array([mach_data_sub[-1], mach_data_sup[0]])#, mach_data_sup[1]])
        mach_data_trans_CDinviscnvisc  = np.array([mach_data_sub[-1], mach_data_sup[0]])#, mach_data_sup[1]])

        cl_surrogate_sub               = RectBivariateSpline(AoA_data, mach_data_sub, CL_data_sub, kx=2, ky=2)  
        cl_surrogate_trans             = RegularGridInterpolator((AoA_data, mach_data_trans_CL), CL_data_trans, \
                                                                 method = 'linear', bounds_error=False, fill_value=None)  
        
        cd_surrogate_sub               = RectBivariateSpline(AoA_data, mach_data_sub, CDinviscnvisc_data_sub, kx=2, ky=2)      
        cd_surrogate_trans             = RegularGridInterpolator((AoA_data, mach_data_trans_CDinviscnvisc), CDinviscnvisc_data_trans, \
                                                                 method = 'linear', bounds_error=False, fill_value=None)

        if lenMachSup > 2: # Sets different interpolation orders depending on how many data points you have. 2nd Order for 3 or more in supersonic
            cl_surrogate_sup               = RectBivariateSpline(AoA_data, mach_data_sup, CL_data_sup, kx=2, ky=2)
            cd_surrogate_sup               = RectBivariateSpline(AoA_data, mach_data_sup, CDinviscnvisc_data_sup, kx=2, ky=2)
        else: 
            if lenMachSup == 1: # If you only have one supersonic set, spoof a second set to enable the interpolation, essentially a 0th order interp
                new_CL_data_sup = np.append(CL_data_sup, CL_data_sup, axis=1)
                new_CDinviscnvisc_data_sup = np.append(CDinviscnvisc_data_sup, CDinviscnvisc_data_sup, axis=1)
                new_mach_data_sup = np.append(mach_data_sup, mach_data_sup[0]+0.1)

                #Bounding box to prevent interpolation outside of range. Down to zero so it won't cause issues when splining the surrogates together for calcs

                cl_surrogate_sup        = RectBivariateSpline(AoA_data, new_mach_data_sup, new_CL_data_sup, kx=2, ky=1, bbox=[None, None, 0.0, new_mach_data_sup[1]]) 
                cd_surrogate_sup        = RectBivariateSpline(AoA_data, new_mach_data_sup, new_CDinviscnvisc_data_sup, kx=2, ky=1, bbox=[None, None, 0.0, new_mach_data_sup[1]])

            else: #If you have two pieces of data, do actual 1st order

                cl_surrogate_sup        = RectBivariateSpline(AoA_data, mach_data_sup, CL_data_sup, kx=2, ky=1, bbox=[None, None, 0.0, mach_data_sup[1]]) 
                cd_surrogate_sup        = RectBivariateSpline(AoA_data, mach_data_sup, CDinviscnvisc_data_sup, kx=2, ky=1, bbox=[None, None, 0.0, mach_data_sup[1]])




        #### Find aerodynamic center


        #Set stuff up to be able to find AC
        min_mach = np.amin(xy[:,1])

        length = xy.shape[0]

        counter = 0

        #try:
        #    print('Aerodynamic Center was set previously to: ', self.geometry.aerodynamic_center)
        #except:
        for i in range(0,length):
            if xy[i,1]==min_mach and counter==1:
                upper_aoa    = xy[i,0]
                upper_cl     = CL_data[i]
                upper_cm     = CM_data[i]
                break
            elif xy[i,1]==min_mach and counter==0:
                lower_aoa    = xy[i,0]
                lower_cl     = CL_data[i]
                lower_cm     = CM_data[i]
                counter     += 1

        CL_slope = (upper_cl - lower_cl)/(upper_aoa - lower_aoa)
        CM_slope = (upper_cm - lower_cm)/(upper_aoa - lower_aoa)

        x_ac = -1*(CM_slope/CL_slope) + 0.25

        self.storage.aerodynamic_center = x_ac




        #### Pack up surrogates
      
        #Saving surrogates to the places they are needed        
        self.surrogates.lift_coefficient_subsonic = cl_surrogate_sub
        self.surrogates.lift_coefficient_supersonic = cl_surrogate_sup
        self.surrogates.lift_coefficient_transonic = cl_surrogate_trans
        self.surrogates.drag_coefficient_subsonic = cd_surrogate_sub
        self.surrogates.drag_coefficient_supersonic = cd_surrogate_sup
        self.surrogates.drag_coefficient_transonic = cd_surrogate_trans


        return


    def plot_surrogate(self):
        """Plots the surrogate on a contour plot
        -Hopefully will expand this in the future with plotting options as inputs

        Assumptions:
        -Surrogate is already built
        -Currently setup only to plot for surrogate done with RectBivariateSpline and RegularGridInterpolator (for transonic), no longer works for GaussianProcessRegressor

        Source:
        N/A

        Inputs:
        self.training.
        coefficients     [-] CL and CD
        grid_points      [radians,-] angles of attack and mach numbers 

        Outputs:
        self.surrogates.
        lift_coefficient <Guassian process surrogate>
        drag_coefficient <Guassian process surrogate>

        Properties Used:
        No others
        """

        # Unpack data
        training  = self.training
        AoA_data  = training.angle_of_attack
        mach_data = training.Mach
        CL_data   = training.coefficients[:,0]
        CD_data   = training.coefficients[:,1]
        CM_data   = training.coefficients[:,2]
        xy        = training.grid_points # [AOA, Mach]

        hsub_min    = self.hsub_min
        hsub_max    = self.hsub_max
        hsup_min    = self.hsup_min
        hsup_max    = self.hsup_max

        # Unpack surrogates

        surrogates = self.surrogates
        CL_surrogate_sub          = surrogates.lift_coefficient_subsonic  
        CL_surrogate_sup          = surrogates.lift_coefficient_supersonic  
        CL_surrogate_trans        = surrogates.lift_coefficient_transonic
        CDinviscnvisc_surrogate_sub         = surrogates.drag_coefficient_subsonic  
        CDinviscnvisc_surrogate_sup         = surrogates.drag_coefficient_supersonic  
        CDinviscnvisc_surrogate_trans       = surrogates.drag_coefficient_transonic

        # Spline for Subsonic-to-Transonic-to-Supesonic Regimes
        sub_trans_spline = Cubic_Spline_Blender(hsub_min,hsub_max)
        h_sub            = lambda M:sub_trans_spline.compute(M)          
        sup_trans_spline = Cubic_Spline_Blender(hsup_min,hsup_max) 
        h_sup            = lambda M:sup_trans_spline.compute(M) 

        # Plot the surrogate

        # Resets plot to whatever your actual surrogate range is, plus 50% on either end
        range_aoa = np.absolute(xy[0,0] - xy[-1,0]) * 0.5
        range_mach = np.absolute(xy[0,1] - xy[-1,1]) * 0.5

        low_aoa = (xy[0,0] - range_aoa) / Units.deg
        high_aoa = (xy[-1,0] + range_aoa) / Units.deg

        low_mach = xy[0,1] - range_mach
        high_mach = xy[-1,1] + range_mach

        #New adaptive plotting 
        AoA_points = np.linspace(low_aoa,high_aoa,100)*Units.deg
        mach_points = np.linspace(low_mach,high_mach,100)          
            
        AoA_mesh,mach_mesh = np.meshgrid(AoA_points,mach_points)
            
        CL_sur = np.zeros(np.shape(AoA_mesh))
        CD_sur = np.zeros(np.shape(AoA_mesh))        
            
        for jj in range(len(AoA_points)):
            for ii in range(len(mach_points)):
                CL_sur[ii,jj] = h_sub( np.atleast_2d(mach_mesh[ii,jj]) )*CL_surrogate_sub(AoA_mesh[ii,jj], mach_mesh[ii,jj],grid=False) +\
                    ( h_sup( np.atleast_2d(mach_mesh[ii,jj]) ) - h_sub( np.atleast_2d(mach_mesh[ii,jj]) ) ) * CL_surrogate_trans((AoA_mesh[ii,jj],mach_mesh[ii,jj])) +\
                    (1- h_sup( np.atleast_2d(mach_mesh[ii,jj]) ))*CL_surrogate_sup(AoA_mesh[ii,jj],mach_mesh[ii,jj],grid=False)

                CD_sur[ii,jj] = h_sub( np.atleast_2d(mach_mesh[ii,jj]) )*CDinviscnvisc_surrogate_sub(AoA_mesh[ii,jj], mach_mesh[ii,jj],grid=False)   +\
                    (h_sup( np.atleast_2d(mach_mesh[ii,jj]) ) - h_sub( np.atleast_2d(mach_mesh[ii,jj]) ))*CDinviscnvisc_surrogate_trans((AoA_mesh[ii,jj],mach_mesh[ii,jj]))+ \
                    (1- h_sup( np.atleast_2d(mach_mesh[ii,jj]) ))*CDinviscnvisc_surrogate_sup(AoA_mesh[ii,jj], mach_mesh[ii,jj],grid=False)
            

        fig = plt.figure('Coefficient of Lift Surrogate Plot')    
        plt_handle = plt.contourf(AoA_mesh/Units.deg,mach_mesh,CL_sur,levels=21)
        #plt.clabel(plt_handle, inline=1, fontsize=10)
        cbar = plt.colorbar()
        plt.scatter(xy[:,0]/Units.deg,xy[:,1])
        plt.xlabel('Angle of Attack (deg)')
        plt.ylabel('Mach Number')
        cbar.ax.set_ylabel('Coefficient of Lift')

        # Stub for plotting drag if implemented:

        drag_levels = np.linspace(0,0.14,21)

        fig = plt.figure('Coefficient of Drag Surrogate Plot')    
        plt_handle = plt.contourf(AoA_mesh/Units.deg,mach_mesh,CD_sur,levels=drag_levels)
        #plt.clabel(plt_handle, inline=1, fontsize=10)
        cbar = plt.colorbar()
        plt.scatter(xy[:,0]/Units.deg,xy[:,1])
        plt.xlabel('Angle of Attack (deg)')
        plt.ylabel('Mach Number')
        cbar.ax.set_ylabel('Coefficient of Drag')

        #plt.contourf(AoA_mesh/Units.deg,mach_mesh,CD_sur,levels=None)
        #plt.colorbar()
        #plt.xlabel('Angle of Attack (deg)')
        #plt.ylabel('Mach Number')   
            
        plt.show() 

        return






# ----------------------------------------------------------------------
#  Helper Functions
# ----------------------------------------------------------------------

def call_SU2(conditions,settings,geometry):
    """Calculates lift and drag using SU2

    Assumptions:
    None

    Source:
    N/A

    Inputs:
    conditions.
      mach_number        [-]
      angle_of_attack    [radians]
    settings.
      half_mesh_flag     <boolean> Determines if a symmetry plane is used
      parallel           <boolean>
      processors         [-]
      maximum_iterations [-]
    geometry.
      tag
      reference_area     [m^2]

    Outputs:
    CL                   [-]
    CD                   [-]

    Properties Used:
    N/A
    """

    half_mesh_flag = settings.half_mesh_flag
    tag            = geometry.tag
    parallel       = settings.parallel
    processors     = settings.processors 
    iters          = settings.maximum_iterations
    
    SU2_settings = Data()
    if half_mesh_flag == False:
        SU2_settings.reference_area  = geometry.reference_area
    else:
        SU2_settings.reference_area  = geometry.reference_area/2.
    SU2_settings.mach_number     = conditions.aerodynamics.mach
    try:
        SU2_settings.x_moment_origin = geometry.fuselages['fuselage'].lengths.total * 0.25
    except:
        print('No fuselage length found in call_SU2! Setting to 0')
        SU2_settings.x_moment_origin = 0.0

    SU2_settings.angle_of_attack = conditions.aerodynamics.angle_of_attack / Units.deg
    SU2_settings.maximum_iterations = iters

    SU2_settings.physical_prob = settings.physical_problem
    if SU2_settings.physical_prob == 'NAVIER_STOKES':
        SU2_settings.turb_model = settings.turb_model
    else:
        SU2_settings.turb_model = None
    
    # Build SU2 configuration file
    write_SU2_cfg(tag, SU2_settings)
    
    # Run SU2
    CL, CD, CM = call_SU2_CFD(tag,parallel,processors)
        
    return CL, CD, CM
