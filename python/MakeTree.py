#!/usr/bin/env python

from ROOT import TFile, TTree, TGraph, TCanvas
import numpy
from array import array
import sys
from SRWToolsUtil import *

InFileName = sys.argv[1]
OutFileName = sys.argv[2]

fi = open(InFileName, 'r')
fo = TFile(OutFileName, 'recreate')
t  = TTree('mmlabdata', 'mmlabdata')

tZ  = numpy.zeros(1, dtype=float)
tBx = numpy.zeros(1, dtype=float)
tBy = numpy.zeros(1, dtype=float)
tBz = numpy.zeros(1, dtype=float)

t.Branch('Z',  tZ,  'Z')
t.Branch('Bx', tBx, 'Bx')
t.Branch('By', tBy, 'By')
t.Branch('Bz', tBz, 'Bz')

Z  = array('d')
Bx = array('d')
By = array('d')
Bz = array('d')


for l in fi:
  [tZ[0], tBx[0], tBy[0], tBz[0]] = map(float, l.split())

  # make in SI unites
  tZ[0] /= 1000.
  t.Fill()

  Z.append(tZ[0])
  Bx.append(tBx[0])
  By.append(tBy[0])
  Bz.append(tBz[0])



# Loop over data and find min/max for every point
LastBy = 0
UpStart = False
DownStart = False
MaxBy = 0
MinBy = 0
MaxByPos = 0
MinByPos = 0
for i in range( len(Z) ):
  if LastBy < 0.002 and By[i] > 0.02:
    UpStart = True
    DownStart = False
    MaxBy = 0
    MaxByPos = 0
  if LastBy > 0.002 and By[i] < 0.02:
    UpStart = False
    DownStart = True
    MinBy = 0
    MinByPos = 0
    print MaxByPos, MaxBy
    MaxBy = 0

  if UpStart and By[i] > MaxBy:
    MaxBy = By[i]
    MaxByPos = Z[i]






gBx = TGraph( len(Z), Z, Bx )
gBy = TGraph( len(Z), Z, By )
gBz = TGraph( len(Z), Z, Bz )

gBx.SetTitle('Measured magnetic field B_{X}')
gBx.GetXaxis().SetTitle('Position [m]')
gBx.GetYaxis().SetTitle('#B_{x} [T]')
gBx.SetName("Bx")

gBy.SetTitle('Measured magnetic field B_{Y}')
gBy.GetXaxis().SetTitle('Position [m]')
gBy.GetYaxis().SetTitle('B_{Y} [T]')
gBy.SetName("By")

gBz.SetTitle('Measured magnetic field B_{Z}')
gBz.GetXaxis().SetTitle('Position [m]')
gBz.GetYaxis().SetTitle('B_{Z} [T]')
gBz.SetName("Bz")

gBx.Write()
gBy.Write()
gBz.Write()



# this is the particle which will travel through the field
part = SRWLParticle()
part.x     =  0.0 # Initial position x [m]
part.y     =  0.0 # Initial position y [m]
part.xp    =  0.0 # Iitial velocity
part.yp    =  0.0 # Initial velocity
part.gamma =  3/0.51099890221e-03 # Relative Energy
part.relE0 =  1 # Electron Rest Mass
part.nq    = -1 # Electron Charge



# Defining Magnetic Field container:
magFldCnt = SRWLMagFldC()
magFldCnt.allocate(1)


# Read data from file and make mag field object
magFldCnt.arMagFld[0] = ReadHallProbeDataSRW(InFileName)

# Field interpolation method
magFldCnt.arMagFld[0].interp = 4

# ID center
magFldCnt.arXc[0] = 0.0
magFldCnt.arYc[0] = 0.0


# Number of reps of field
magFldCnt.arMagFld[0].nRep = 1

# Center in Z of ID
magFldCnt.arZc[0] = 0.0

# Starting position in z of particle
part.z = 0.0 - 0.5*magFldCnt.arMagFld[0].rz

# Trajectory structure, where the results will be stored
partTraj = SRWLPrtTrj()
partTraj.partInitCond = part

# Number of trajectory points
partTraj.allocate(10001, True)
partTraj.ctStart = 0
partTraj.ctEnd = magFldCnt.arMagFld[0].rz


# Calculation (SRWLIB function call)
partTraj = srwl.CalcPartTraj(partTraj, magFldCnt, [1])

# Get the Z Values for the plot
ZValues = [float(x) * ((partTraj.ctEnd - partTraj.ctStart) / float(partTraj.np)) for x in range(0, partTraj.np)]

# Convert to mm from m
for i in range(partTraj.np):
    partTraj.arX[i] *= 1000
    partTraj.arY[i] *= 1000
 

gElectronX = TGraph( len(ZValues), array('d', ZValues), partTraj.arX)
gElectronY = TGraph( len(ZValues), array('d', ZValues), partTraj.arY)

gElectronX.SetTitle('Electron Trajectory in X')
gElectronX.GetXaxis().SetTitle('Z Position [m]')
gElectronX.GetYaxis().SetTitle('X Position [m]')
gElectronX.SetName("ElectronX")

gElectronY.SetTitle('Electron Trajectory in Y')
gElectronY.GetXaxis().SetTitle('Z Position [m]')
gElectronY.GetYaxis().SetTitle('Y Position [m]')
gElectronY.SetName("ElectronY")

gElectronX.Write()
gElectronY.Write()








# Defining Magnetic Field container:
magFldCnt = SRWLMagFldC()
magFldCnt.allocate(1)

# define the undulator specs
numPer = 70
undPer = 0.021
Bx = 0.0
By = 1.0
phBx = 0
phBy = 0
sBx = 1
sBy = 1
xcID = 0
ycID = 0
zcID = 0

und = SRWLMagFldU([SRWLMagFldH(1, 'v', By, phBy, sBy, 1), SRWLMagFldH(1, 'h', Bx, phBx, sBx, 1)], undPer, numPer)
magFldCnt = SRWLMagFldC([und], array('d', [xcID]), array('d', [ycID]), array('d', [zcID])) #Container of all Field Elements


[SpectrumIdealX, SpectrumIdealY] = GetUndulatorSpectrum(magFldCnt)

gSpectrumIdeal = TGraph( len(SpectrumIdealX), array('d', SpectrumIdealX), array('d', SpectrumIdealY) )
gSpectrumIdeal.SetName('SpectrumIdeal')
gSpectrumIdeal.SetTitle('Simulated B-field Spectrum')
gSpectrumIdeal.GetXaxis().SetTitle('Energy [eV]')
gSpectrumIdeal.GetYaxis().SetTitle('Intensity photons/s/.1%bw/mm^{2}')
gSpectrumIdeal.Write()





# Read data from file and make mag field object
magFldCnt.arMagFld[0] = ReadHallProbeDataSRW(InFileName)

# Field interpolation method
magFldCnt.arMagFld[0].interp = 4

# ID center
magFldCnt.arXc[0] = 0.0
magFldCnt.arYc[0] = 0.0


# Number of reps of field
magFldCnt.arMagFld[0].nRep = 1

# Center in Z of ID
magFldCnt.arZc[0] = 0.0



[SpectrumX, SpectrumY] = GetUndulatorSpectrum(magFldCnt)

gSpectrum = TGraph( len(SpectrumX), array('d', SpectrumX), array('d', SpectrumY) )
gSpectrum.SetName('Spectrum')
gSpectrum.SetTitle('Simulated B-field Spectrum')
gSpectrum.GetXaxis().SetTitle('Energy [eV]')
gSpectrum.GetYaxis().SetTitle('Intensity photons/s/.1%bw/mm^{2}')
gSpectrum.Write()


fo.Write()
fo.Close()
