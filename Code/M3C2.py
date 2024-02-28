#!/usr/bin/env python3

##########################################################################
#                                                                        #
#                              CloudComPy                                #
#                                                                        #
#  This program is free software; you can redistribute it and/or modify  #
#  it under the terms of the GNU General Public License as published by  #
#  the Free Software Foundation; either version 3 of the License, or     #
#  any later version.                                                    #
#                                                                        #
#  This program is distributed in the hope that it will be useful,       #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          #
#  GNU General Public License for more details.                          #
#                                                                        #
#  You should have received a copy of the GNU General Public License     #
#  along with this program. If not, see <https://www.gnu.org/licenses/>. #
#                                                                        #
#          Copyright 2020-2021 Paul RASCLE www.openfields.fr             #
#                                                                        #
##########################################################################

import os
import sys
import math

os.environ["_CCTRACE_"]="ON" # only if you want C++ debug traces

from gendata import getSampleCloud, dataDir, isCoordEqual
import cloudComPy as cc
import numpy as np
#---M3C2params01-begin
import multiprocessing

m3c2_params_dic={}
m3c2_params_dic["ExportDensityAtProjScale"] = "false"
m3c2_params_dic["ExportStdDevInfo"] = "false"
m3c2_params_dic["M3C2VER"] = 1
m3c2_params_dic["MaxThreadCount"] = multiprocessing.cpu_count()
m3c2_params_dic["MinPoints4Stat"] = 5
m3c2_params_dic["NormalMaxScale"] = 0.283607
m3c2_params_dic["NormalMinScale"] = 0.070902
m3c2_params_dic["NormalMode"] = 0
m3c2_params_dic["NormalPreferedOri"] = 4
m3c2_params_dic["NormalScale"] = 0.141803
m3c2_params_dic["NormalStep"] = 0.070902
m3c2_params_dic["NormalUseCorePoints"] = "false"
m3c2_params_dic["PM1Scale"] = 1
m3c2_params_dic["PM2Scale"] = 1
m3c2_params_dic["PositiveSearchOnly"] = "false"
m3c2_params_dic["ProjDestIndex"] = 1
m3c2_params_dic["RegistrationError"] = 0
m3c2_params_dic["RegistrationErrorEnabled"] = "false"
m3c2_params_dic["SearchDepth"] = 0.709017
m3c2_params_dic["SearchScale"] = 0.141803
m3c2_params_dic["SubsampleEnabled"] = "true"
m3c2_params_dic["SubsampleRadius"] = 0.070902
m3c2_params_dic["UseMedian"] = "false"
m3c2_params_dic["UseMinPoints4Stat"] = "false"
m3c2_params_dic["UseOriginalCloud"] = "false"
m3c2_params_dic["UsePrecisionMaps"] = "false"
m3c2_params_dic["UseSinglePass4Depth"] = "false"

paramFilename1 = os.path.join(dataDir, "m3c2_params1.txt")
with open(paramFilename1, 'w') as f:
    f.write("[General]\n")
    for k,v in m3c2_params_dic.items():
        f.write("%s=%s\n"%(k,v))
#---M3C2params01-end

#---computeM3C2_01-begin
if cc.isPluginM3C2():
    import cloudComPy.M3C2
    epoch1 = cc.loadPointCloud(getSampleCloud(5.0))
    epoch2 = cc.loadPointCloud(getSampleCloud(1.0))
    paramFilename = os.path.join(dataDir, "m3c2_params.txt")
    ret = cc.M3C2.M3C2guessParamsToFile([epoch1,epoch2], paramFilename, True)
    epoch3 = cc.M3C2.computeM3C2([epoch1,epoch2], paramFilename)
#---computeM3C2_01-end
    
    if epoch3 is None:
        raise RuntimeError
    if epoch3.getNumberOfScalarFields() < 3:
        raise RuntimeError
    dic= epoch3.getScalarFieldDic()
    sf = epoch3.getScalarField(dic['M3C2 distance'])
    if sf is None:
        raise RuntimeError
    if not math.isclose(sf.getMax(), 0.71, rel_tol=0.02):
        raise RuntimeError
    if not math.isclose(sf.getMin(), -0.71, rel_tol=0.02):
        raise RuntimeError

    cc.SaveEntities([epoch1, epoch2, epoch3], os.path.join(dataDir, "M3C2.bin"))

    npts = 1000000
    x = np.float32(-5 +10*np.random.random((npts)))
    y = np.float32(-5 +10*np.random.random((npts)))
    f = np.sqrt(x*x + y*y)
    u = 0.005*f
    z = np.sin(3*f)/(f+1.e-6) + 2*u*(0.5-np.random.random((npts)))
    d = np.zeros(npts)
    coords = np.column_stack((x,y,z))
    epoch1 = cc.ccPointCloud("epoch1")
    epoch1.coordsFromNPArray_copy(coords)
    epoch1.addScalarField("ux")
    epoch1.addScalarField("uy")
    epoch1.addScalarField("uz")
    sfx = epoch1.getScalarField(0)
    sfx.fromNpArrayCopy(d)
    sfy = epoch1.getScalarField(1)
    sfy.fromNpArrayCopy(d)
    sfz = epoch1.getScalarField(2)
    sfz.fromNpArrayCopy(u)

    npts = 1000000
    x = np.float32(-5 +10*np.random.random((npts)))
    y = np.float32(-5 +10*np.random.random((npts)))
    f = np.sqrt(x*x + y*y)
    u = 0.01*f
    z = 0.2+np.sin(3*f)/(f+1.e-6) + 2*u*(0.5-np.random.random((npts)))
    d = np.zeros(npts)
    coords = np.column_stack((x,y,z))
    epoch2 = cc.ccPointCloud("epoch2")
    epoch2.coordsFromNPArray_copy(coords)
    epoch2.addScalarField("ux")
    epoch2.addScalarField("uy")
    epoch2.addScalarField("uz")
    sfx = epoch2.getScalarField(0)
    sfx.fromNpArrayCopy(d)
    sfy = epoch2.getScalarField(1)
    sfy.fromNpArrayCopy(d)
    sfz = epoch2.getScalarField(2)
    sfz.fromNpArrayCopy(u)

#---computeM3C2_02-begin
    sfs = []
    dic = epoch1.getScalarFieldDic()
    sfs.append(epoch1.getScalarField(dic["ux"]))
    sfs.append(epoch1.getScalarField(dic["uy"]))
    sfs.append(epoch1.getScalarField(dic["uz"]))
    dic1 = epoch2.getScalarFieldDic()
    sfs.append(epoch2.getScalarField(dic1["ux"]))
    sfs.append(epoch2.getScalarField(dic1["uy"]))
    sfs.append(epoch2.getScalarField(dic1["uz"]))
    scales = [1., 1.]
    paramFilename = os.path.join(dataDir, "m3c2_params2.txt")
    ret = cc.M3C2.M3C2guessParamsToFile([epoch1,epoch2], paramFilename, True)
    epoch3 = cc.M3C2.computeM3C2([epoch1,epoch2], paramFilename, sfs, scales)
#---computeM3C2_02-end
    
    dic= epoch3.getScalarFieldDic()
    sf = epoch3.getScalarField(dic['distance uncertainty'])
    if sf is None:
        raise RuntimeError
    mean,var = sf.computeMeanAndVariance()
    if not math.isclose(mean, 0.0682, rel_tol=0.01):
        raise RuntimeError

    cc.SaveEntities([epoch1, epoch2, epoch3], os.path.join(dataDir, "Experiment1b.bin"))
