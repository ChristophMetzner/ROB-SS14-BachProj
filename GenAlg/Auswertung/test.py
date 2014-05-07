def calc_dens(chromosome,mode,BS):
	# chromosome = [ar, cal, cat, k2, ka,(kaib), kahp, kc, kdr, km, naf, nap, pas]
	list = []

	if mode == 1 or mode == 2:
		ar = [-1.0, 1.0, 2.0] 
		for v in ar:
			if v == -1.0:
				list.append(v)
			else:
				list.append(v*chromosome[0])
		cal = [1.6, 0.32] 
		for v in cal:
			list.append(v*chromosome[1])
		cat = [1.0, 2.0]
		for v in cat:
			list.append(v*chromosome[2])
		k2 = [1.0,0.5] 
		for v in k2:
			list.append(v*chromosome[3])
		ka = [1.6, 2.0, 0.06] 
		for v in ka:
			list.append(v*chromosome[4])
		kahp = [2.0, 4.0]
		for v in kahp:
			list.append(v*chromosome[5])
		kc = [1.2, 2.88] 
		for v in kc:
			list.append(v*chromosome[6])
		kdr = [1.5, 1.7, 4.5]
		for v in kdr:
			list.append(v*chromosome[7])
		km = [ 3.0, 0.75, 0.85] 
		for v in km:
			list.append(v*chromosome[8])
		naf = [ -1.0, 1.875, 2.0, 4.5] 
		for v in naf:
			if v == -1.0:
				list.append(v)
			else:
				list.append(v*chromosome[9])
		nap = [ 1.0, 1.6] 
		for v in nap:
			list.append(v*chromosome[10])
		pas = [-1.0, 1.0, 0.02, 0.3] 
		for v in pas:
			if v == -1.0:
				list.append(v)
			else:
				list.append(v*chromosome[11])
	else: #3,4
		ar = [-1.0, 0.1, 0.1] 
		for v in ar:
			if v == -1.0:
				list.append(v)
			else:
				list.append(v*chromosome[0])
		cal = [4.0, 4.0] 
		for v in cal:
			list.append(v*chromosome[1])
		cat = [0.1, 0.1]
		for v in cat:
			list.append(v*chromosome[2])
		k2 = [0.5, 0.5] 
		for v in k2:
			list.append(v*chromosome[3])
		kaib = [ 0.6, 0.6, 20] 
		for v in kaib:
			list.append(v*chromosome[4])
		kahp = [0.2, 0.2]
		for v in kahp:
			list.append(v*chromosome[5])
		kc = [ 0.5,16] 
		for v in kc:
			list.append(v*chromosome[6])
		kdr = [ 75, 170, 450] 
		for v in kdr:
			list.append(v*chromosome[7])
		km = [ 19.04, 11.9, 42]
		for v in km:
			list.append(v*chromosome[8])
		naf = [-1.0, 15, 75,200] 
		for v in naf:
			if v == -1.0:
				list.append(v)
			else:
				list.append(v*chromosome[9])
		nap = [ 0, 0.012] 
		for v in nap:
			list.append(v*chromosome[10])
		pas = [-1.0, 0, 0, 0] 
		for v in pas:
			if v == -1.0:
				list.append(v)
			else:
				list.append(v*chromosome[11])
	if BS == 1:
		density = open("./Bachelorarbeit/Auswertung/density.txt","w")
	else:
		density = open("C:\Python27\Bachelorarbeit\Auswertung\density.txt","w")
	string = ''
	for e in list:
		string += str(e)+'\n'
	density.write(string+'#\n')
	density.close()
	
#endDEF
