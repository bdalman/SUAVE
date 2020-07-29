import sys, os

sys.path.append(os.path.abspath("/home/bwdalman/Documents/OFSimManager/SimpleRunScripts/"))

from gridConvergenceFunctions import checkConvergence

def check_grid_convergence(coarse, med, fine, refineRatio):

	ordersOfConvergence, GCI12s, GCI23s, asymptoticChecks, richardsonExtrapVals, uncertainties = checkConvergence(coarse, med, fine, refineRatio, minConvergOrder=0.1, maxConvergOrder=4, theoreticalOrderOfConvergence=1)
	print(ordersOfConvergence)
	print(GCI12s)
	print(GCI23s)
	print(asymptoticChecks)
	print(uncertainties)

	return richardsonExtrapVals