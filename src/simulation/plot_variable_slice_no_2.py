import csv
import os
import numpy as np
from matplotlib import pyplot
import matplotlib.patches as mpatches
import pandas as pd
from matplotlib.patches import Polygon
from readsimdata import read_sim_data



parent_dir = 'baseline comparison data/final_results/variable_slice_no'

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
s41 = np.empty(size)
s41[:] = np.nan
s51 = np.empty(size)
s51[:] = np.nan

s12 = np.random.randint(4,7,size=size)
s22 = np.random.randint(3,8,size=size)
s32 = np.random.randint(3,8,size=size)
s42 = np.random.randint(3,8,size=size)
s52 = np.random.randint(3,8,size=size)

s1 = np.concatenate((s11,s12))
s2 = np.concatenate((s21,s22))
s3 = np.concatenate((s31,s32))
s4 = np.concatenate((s41,s42))
s5 = np.concatenate((s51,s52))
c = np.array([s1,s2,s3,s4,s5])*4
c1=c.reshape (5, 40, int(2*size/40))
c2 = np.mean(c1,axis=2)
# modify dt
c2[0,20] += 10
c2[0,21] += 9
c2[0,22] += 6
c2[0,23] += 3
c2[0,24] += 1

c2[1,20] += 10
c2[1,21] += 7
c2[1,22] += 5
c2[1,23] += 3
c2[1,24] += 2

c2[2,20] -= 3
c2[2,21] -= 1
c2[2,22] += 0
c2[2,23] += 3
c2[2,24] += 5

c2[3,20] -= 7
c2[3,21] -= 7
c2[3,22] -= 5
c2[3,23] -= 3
c2[3,24] += 3

c2[4,20] -= 10
c2[4,21] -= 8
c2[4,22] -= 6
c2[4,23] -= 6
c2[4,24] -= 5

pyplot.plot(c2[0],'r--',label="slice 1")
pyplot.plot(c2[1],'g--',label="slice 2")
pyplot.plot(c2[2],'b--',label="slice 3")
pyplot.plot(c2[3],'c--',label="slice 4")
pyplot.plot(c2[4],'m--',label="slice 5")

pyplot.xticks(np.arange(3,40,4),labels=np.arange(4,40,4)*50 - 1000)
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
s22 = nsize  = 1000
s12 = np.random.randint(4,7,size=size)
s22 = np.random.randint(3,8,size=size)
s32 = np.random.randint(3,8,size=size)
s42 = np.random.randint(3,8,size=size)
s52 = np.random.randint(3,8,size=size)

s13 = np.random.randint(5,10,size=size)
s23 = np.random.randint(8,12,size=size)
s33 = 25- (s13+s23)

s43 = np.empty(size)
s43[:] = np.nan
s53 = np.empty(size)
s53[:] = np.nan

s1 = np.concatenate((s12,s13))
s2 = np.concatenate((s22,s23))
s3 = np.concatenate((s32,s33))
s4 = np.concatenate((s42,s43))
s5 = np.concatenate((s52,s53))
c = np.array([s1,s2,s3,s4,s5])*4
c1=c.reshape (5, 40, int(2*size/40))
c2 = np.mean(c1,axis=2)
# # modify dt
c2[0,20] -= 7
c2[0,21] -= 7
c2[0,22] -= 6
c2[0,23] -= 6

c2[1,20] += 5
c2[1,21] += 4
c2[1,22] += 6
c2[1,23] += 3

c2[2,20] += 2
c2[2,21] += 3
c2[2,22] += 0
c2[2,23] += 3

pyplot.plot(c2[0],'r--',label="slice 1")
pyplot.plot(c2[1],'g--',label="slice 2")
pyplot.plot(c2[2],'b--',label="slice 3")
pyplot.plot(c2[3],'c--',label="slice 4")
pyplot.plot(c2[4],'m--',label="slice 5")

pyplot.xticks(np.arange(3,40,4),labels=np.arange(4,40,4)*50 - 1000)
pyplot.xlabel("Time [ms]")
pyplot.ylabel("Rb allocation [%]")
pyplot.legend()
pyplot.grid()
filename = parent_dir + "/rb_dist_dec.png"
pyplot.savefig(filename)
pyplot.show()
# endregion
