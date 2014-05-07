#! usr/local/lib/python2.7 python
# coding=utf-8
import sys
#sys.path.append("C:\Python27\Bachelorarbeit\Auswertung")
sys.path.append("./GenAlg/Auswertung/")

import FFT

BS  = 1

if BS == 1:
	execfile("./GenAlg/Auswertung/chrom_in_dens.py")
else:
	execfile("C:\Python27\GenAlg\Auswertung\chrom_in_dens.py")

FFT.Fourier(	Anzahl = 1,
			modus = 1,
			currents = [1,0.2,1],
			simulieren =0, 
			BS = BS)
