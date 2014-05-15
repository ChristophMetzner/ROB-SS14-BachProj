

'''
File to convert makeSyns.sh to makeSyns.bat for windows...
'''

fileSh = open("makeSyns.sh",'r')
fileBat = open("makeSyns.bat",'w')

for line in fileSh:
    if "#" in line:
        newLine = line.split("#")[0].strip()
    else:
        newLine = line.strip()

    newLine = newLine.replace("rm -rf", "del ")
    if len(newLine)>0:
        print newLine
        fileBat.write(newLine+"\n")

fileBat.close()