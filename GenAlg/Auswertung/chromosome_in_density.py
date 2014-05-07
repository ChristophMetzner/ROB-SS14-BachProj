import sys
#sys.path.append("C:\Python27\GenAlg\Auswertung")
sys.path.append("./Bachelorarbeit/Auswertung/")
import calc_density
#import subprocess
BS = 1

if BS == 1:
	filename = "./GenAlg/Auswertung/Config.txt"
else:
	filename = "C:\Python27\GenAlg\Auswertung\Config.txt"
config = open(filename, 'r')
c = 0 #counter
mode = 1
for line in config:
	line = line.strip()
	c = c+1	
	if c == 9:
		mode = int(line)
	else:
		pass
config.close()

if BS == 1:
	file = open("./GenAlg/Auswertung/CALCdensity.txt", "r")
	d_list = file.read().split('#\r\n')
else:
	file = open("C:\Python27\GenAlg\Auswertung\CALCdensity.txt", 'r')
	d_list = file.read().split('#\n')


#print d_list
den = d_list[-2].split('\n')

density = []
for d in den:
	d = d.strip()
	try:
		x = float(d)
		density.append(x)
	except:
		pass

	
calc_density.calc_density(density,mode, BS)
file.close()

		
