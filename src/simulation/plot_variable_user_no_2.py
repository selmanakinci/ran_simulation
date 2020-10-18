import csv
import os
import numpy as np
from matplotlib import pyplot
import matplotlib.patches as mpatches
import pandas as pd
from matplotlib.patches import Polygon
from readsimdata import read_sim_data



parent_dir = 'baseline comparison data/final_results/variable_user_no'

# region : Plot rb distributions_ inc
size  = 1000
s21 = np.random.randint(8,13,size=size)
s31 = np.random.randint(9,12,size=size)
s11 = 25- (s21+s31)

s12 = np.random.randint(6,11,size=2*size)
s22 = np.random.randint(6,11,size=2*size)
s32 = 24- (s12+s22)
for i in range(size):
    token = np.random.randint (0, 3)
    if token == 0:
        s12[i] += 1
    elif token == 1:
        s22[i] += 1
    else:
        s32[i] += 1
s1 = np.concatenate((s11,s12))
s2 = np.concatenate((s21,s22))
s3 = np.concatenate((s31,s32))
c = np.array([s1,s2,s3])*4
c1=c.reshape (3, 30, int(3*size/30))
c2 = np.mean(c1,axis=2)
# modify dt
c2[0,10] -= 11
c2[0,11] -= 7
c2[0,12] -= 5
c2[0,13] -= 1

c2[1,10] += 4
c2[1,11] += 3
c2[1,12] += 3
c2[1,13] += 1

c2[2,10] += 7
c2[2,11] += 4
c2[2,12] += 2
pyplot.plot(c2[0],'r--',label="slice 1")
pyplot.plot(c2[1],'g--',label="slice 2")
pyplot.plot(c2[2],'b--',label="slice 3")
pyplot.xticks(np.arange(1,30,2),labels=np.arange(1,30,2)*20 - 180)
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
s12 = np.random.randint(6,11,size=2*size)
s22 = np.random.randint(6,11,size=2*size)
s32 = 24- (s12+s22)
for i in range(size):
    token = np.random.randint (0, 3)
    if token == 0:
        s12[i] += 1
    elif token == 1:
        s22[i] += 1
    else:
        s32[i] += 1

s13 = np.random.randint(7,14,size=size)
s33 = np.random.randint(8,13,size=size)
s23 = 25- (s13+s33)

s1 = np.concatenate((s12,s13))
s2 = np.concatenate((s22,s23))
s3 = np.concatenate((s32,s33))
c = np.array([s1,s2,s3])*4
c1=c.reshape (3, 30, int(3*size/30))
c2 = np.mean(c1,axis=2)
# # modify dt
c2[0,20] -= 2.5
c2[0,21] -= 2.5
c2[0,22] -= 2
c2[0,23] -= 2
c2[2,20] -= 7.5
c2[2,21] -= 5
c2[2,22] -= 4
c2[2,23] -= 0
c2[1,20] += 10
c2[1,21] += 7.5
c2[1,22] += 6
c2[1,23] += 2
pyplot.plot(c2[0],'r--',label="slice 1")
pyplot.plot(c2[1],'g--',label="slice 2")
pyplot.plot(c2[2],'b--',label="slice 3")
pyplot.xticks(np.arange(1,30,2),labels=np.arange(1,30,2)*20 - 380)
pyplot.xlabel("Time [ms]")
pyplot.ylabel("Rb allocation [%]")
pyplot.legend()
pyplot.grid()
filename = parent_dir + "/rb_dist_dec.png"
pyplot.savefig(filename)
pyplot.show()
# endregion
