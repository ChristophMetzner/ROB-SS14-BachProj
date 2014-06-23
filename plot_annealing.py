#!/usr/bin/env python2.7
import sys
import numpy as np
import matplotlib.pyplot as plt

def main():

    try:
        if len(sys.argv) >= 2:
            file = sys.argv[1]
        else:
            print "Filename expected as parameter."
    except Exception as ex:
        print ex.message
        return 1

    with open(file) as f:
        data = f.read()

    data = data.split("\n")
    data = data[0].split(", ")

    print data

    map(float, data)

    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    ax1.plot(data)
    plt.show()

     #x = [row.split(' ')[0] for row in data]
     #y = [row.split(' ')[1] for row in data]

     #fig = plt.figure()

     #ax1 = fig.add_subplot(111)

     #ax1.set_title("Plot title...")
     #ax1.set_xlabel('your x label..')
     #ax1.set_ylabel('your y label...')

     #ax1.plot(x,y, c='r', label='the data')

     #leg = ax1.legend()

     #plt.show()

if __name__ == "__main__":
    main()
