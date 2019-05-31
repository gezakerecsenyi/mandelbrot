import math
import re
import numpy as np
import scipy.misc as smp
import time
import shutil
import os
import argparse
import matplotlib as mpl
import sys
import matplotlib.pyplot as plt

print()

parser = argparse.ArgumentParser(description='Enter parameters for your custom fractal.')
parser.add_argument('width', metavar='width', type=int, nargs='+',
                    help='the width (in px) of the output image')
parser.add_argument('height', metavar='height', type=int, nargs='+',
                    help='the height (in px) of the output image')
parser.add_argument('-z_height', metavar='complex height', type=int, nargs='+',
                    help='the height of the complex plane')
parser.add_argument('-z_width', metavar='real width', type=int, nargs='+',
                    help='the width of the complex plane')
parser.add_argument('-x_offset', metavar='x offset', type=int, nargs='+',
                    help='offset of the snapshot in the x-axis')
parser.add_argument('-y_offset', metavar='y offset', type=int, nargs='+',
                    help='offset of the snapshot in the y-axis')
parser.add_argument('--save', action="store_true",
                    help='should we save the output file?')
parser.add_argument('-save_location', metavar='save location',type=str,
                    help='where should we save the file (if --save)')
args = parser.parse_args()

height = args.height[0]
width = args.width[0]

zHeight = 4
if (args.z_height):
  zHeight = args.z_height[0]

zWidth = 4
if (args.z_width):
  zWidth = args.z_width[0]

xOff = 0
if (args.x_offset):
  xOff = args.x_offset[0]

yOff = 0
if (args.y_offset):
  yOff = args.y_offset[0]

stepY = zHeight / height
stepX = zWidth / width
maxTries = 600

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    if iteration == total: 
        print()

if os.path.exists("fractalpxls.txt"):
  os.remove("fractalpxls.txt")

f = open("fractalpxls.txt", "w+")

print("Creating blank canvas")

for row in range(height):
    printProgressBar(row, height, prefix = "Canvas creation progress:", suffix = "completed", length=50)
    for cell in range(width):
        f.write("255,255,255 ")

    f.write("\n")

for i in range(99):
  print(" ", end="")

print("\rBlank canvas created")

def colorFader(c1,c2,mix=0):
    c1=np.array(mpl.colors.to_rgb([tc/255 for tc in c1]))
    c2=np.array(mpl.colors.to_rgb([tc/255 for tc in c2]))
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)

def replacen(base, n, sub, new):
    b = base.split(sub)
    b[n] = new
    return sub.join(b)

f.close()

if os.path.exists("newfractalpxls.txt"):
    os.remove("newfractalpxls.txt")

print()

rp = open("newfractalpxls.txt", "w+")
with open("fractalpxls.txt") as fp:
    for row, line in enumerate(fp):
        printProgressBar(row, height, prefix = "Calculation progress:", suffix = "completed", length=50)
        rowHere = (height / (zHeight / 2) - row) * stepY
        newLine = line
        
        for cell in range(width):
            zHere = [rowHere + xOff, (cell - width / (zWidth/ 2)) * stepX + yOff]
            z = zHere
                
            takes = 1
                
            while(takes < maxTries and (math.sqrt(z[0]**2+z[1]**2)<2)):
                z = [(z[0]**2-z[1]**2)+zHere[0], (2*z[0]*z[1])+zHere[1]]
                takes += 1

            thisColor = "#ffffff"

            if (takes > 599):
                thisColor = "#000000"
            elif (takes > 209):
                thisColor = colorFader([110, 0, 140], [255, 255, 255], mix=takes/600)
            elif (takes > 89):
                thisColor = colorFader([0, 0, 255], [110, 0, 140], mix=takes/210)
            elif (takes > 10):
                thisColor = colorFader([125, 165, 0], [0, 0, 255], mix=takes/90)
            elif (takes > 1):
                thisColor = colorFader([255, 230, 210], [125, 165, 0], mix=takes/11)
            elif takes == 1:
            	thisColor = "#ffffff"


            thisColor = thisColor.lstrip("#")
            thisColor = list(int(thisColor[i:i+2], 16) for i in (0, 2, 4))

            newLine = replacen(str(newLine), cell, " ", ",".join(str(v) for v in thisColor))
            
        rp.write(newLine)

    rp.close()
    shutil.move(os.path.join(os.getcwd(), "newfractalpxls.txt"), os.path.join(os.getcwd(), "fractalpxls.txt"))
                    
for i in range(91):
  print(" ", end="")

print("\rDone coloring\r", end="\n")

data = np.zeros((width, height, 3), dtype = np.uint8)

with open("fractalpxls.txt") as fp:
    for row, line in enumerate(fp):
        printProgressBar(row, height, prefix = "Image processing progress:", suffix = "completed", length=50)
        for cell in range(width-1):
          data[cell, height-row-1] = [int(num) for num in line[line.replace(' ', 'c', cell).find(' '):].split(" ")[1].split(",")]

for i in range(95):
  print(" ", end="")

print("\rDone rendering")
print("Opening output")

img = smp.toimage(data)
img.show()
