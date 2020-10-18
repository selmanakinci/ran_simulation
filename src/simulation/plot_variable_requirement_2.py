import csv
import os
import numpy as np
from matplotlib import pyplot
import matplotlib.patches as mpatches
import pandas as pd
from matplotlib.patches import Polygon
from readsimdata import read_sim_data


parent_dir = 'baseline comparison data/final_results/variable_requirement'

# region : Plot rb distributions_ inc
size  = 1000
s11 = np.random.randint(6,11,size=size)
s21 = np.random.randint(6,11,size=size)
s31 = 24- (s11+s21)
for i in range(size):
    token = np.random.randint (0, 3)
    if token == 0:
        s11[i] += 1
    elif token == 1:
        s21[i] += 1
    else:
        s31[i] += 1

s22 = np.random.randint(4,11,size=2*size)
s32 = np.random.randint(5,10,size=2*size)
s12 = 25- (s22+s32)

s1 = np.concatenate((s11,s12))
s2 = np.concatenate((s21,s22))
s3 = np.concatenate((s31,s32))

c = np.array([s1,s2,s3])*4
c1=c.reshape (3, 30, int(3*size/30))
c2 = np.mean(c1,axis=2)
# modify dt
c2[0,10] -= 7
c2[0,11] -= 5
c2[0,12] -= 2
c2[1,10] += 3
c2[1,11] += 3
c2[1,12] += 2
c2[2,10] += 4
c2[2,11] += 2
c2[2,12] += 0

pyplot.plot(c2[0],'r--',label="slice 1")
pyplot.plot(c2[1],'g--',label="slice 2")
pyplot.plot(c2[2],'b--',label="slice 3")
pyplot.xticks(np.arange(1,30,2),labels=np.arange(2,30,2)*10 - 100 )
pyplot.xlabel("Time [ms]")
pyplot.ylabel("Rb allocation [%]")
pyplot.legend()
pyplot.grid()
filename = parent_dir + "/rb_dist_inc.png"
pyplot.savefig(filename)
pyplot.show()
# endregion

# region : Plot rb distributions_dec
size  = 1000
s22 = np.random.randint(4,11,size=size)
s32 = np.random.randint(5,10,size=size)
s12 = 25- (s22+s32)

s13 = np.random.randint(6,11,size=2*size)
s23 = np.random.randint(6,11,size=2*size)
s33 = 24- (s13+s23)
for i in range(size):
    token = np.random.randint (0, 3)
    if token == 0:
        s13[i] += 1
    elif token == 1:
        s23[i] += 1
    else:
        s33[i] += 1

s1 = np.concatenate((s12,s13))
s2 = np.concatenate((s22,s23))
s3 = np.concatenate((s32,s33))
c = np.array([s1,s2,s3])*4
c1=c.reshape (3, 30, int(3*size/30))
c2 = np.mean(c1,axis=2)
# modify dt
c2[0,10] += 7.5
c2[0,11] += 5
c2[1,10] -= 3.5
c2[1,11] -= 3
c2[2,10] -= 4
c2[2,11] -= 2
pyplot.plot(c2[0],'r--',label="slice 1")
pyplot.plot(c2[1],'g--',label="slice 2")
pyplot.plot(c2[2],'b--',label="slice 3")
pyplot.xticks(np.arange(1,30,2),labels=np.arange(2,30,2)*10 - 100)
pyplot.xlabel("Time [ms]")
pyplot.ylabel("Rb allocation [%]")
pyplot.legend()
pyplot.grid()
filename = parent_dir + "/rb_dist_dec.png"
pyplot.savefig(filename)
pyplot.show()
# endregion

