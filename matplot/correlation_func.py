print("Loading...")
import matplotlib

matplotlib.use("TkAgg")
import time
import matplotlib.backends.backend_pdf as pdfback
import numpy as np
import scipy.spatial as space
import math
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from multiprocessing import Pool
import random
import itertools
NUM_PROCESSORS = 8

#from mayavi import mlab
def load(filename):
    print("Loading Coordinates...")

    xs = []#list of x coordinates of galaxies. The coordinates of galaxy zero are (xs[0],ys[0],zs[0])
    ys = []
    zs = []

    with open(filename, "r") as boxfile:
        for line in boxfile:
            if line[0]!="#":
                try:
                    row = line.split(',')
                    xs.append(float(row[14]))
                    ys.append(float(row[15]))
                    zs.append(float(row[16]))
                except ValueError:
                    pass
    return (xs,ys,zs)

"""
def d_p_est(r,dr,actual_kd,random_kd):
    #from http://ned.ipac.caltech.edu/level5/March04/Jones/Jones5_2.html
    #Nrd = N so the factor Nrd/N = 1 and will be left out.
    #DD(r) = average number of pairs
    #DR(r) = average num pairs between random and actual
    lower = r-(dr/2)
    assert(lower >= 0)
    upper = r+(dr/2)

    DD = actual_kd.count_neighbors(actual_kd,np.array([lower,upper]))
    DR = actual_kd.count_neighbors(random_kd,np.array([lower,upper]))
    print('.',end="",flush=True)
    return ((DD[1]-DD[0])/(DR[1]-DR[0]))-1
"""
def hamest(r,dr,actual_list,random_list):
    actual_kd = space.cKDTree(actual_list,3)
    random_kd = space.cKDTree(random_list,3)
    lower = r-(dr/2)
    assert(lower >= 0)
    upper = r+(dr/2)
    DD = actual_kd.count_neighbors(actual_kd,np.array([lower,upper]))
    DR = actual_kd.count_neighbors(random_kd,np.array([lower,upper]))
    RR = random_kd.count_neighbors(random_kd,np.array([lower,upper]))
    print('.',end="",flush=True)
    DDr = DD[1]-DD[0]
    DRr = DR[1]-DR[0]
    RRr = RR[1]-RR[0]
    return (DDr*RRr)/(DRr**2)-1

def hamestunzip(args):
    print(args)
    return hamest(args[0],args[1],args[2],args[3])

    
def makeplot(xs,ys,title,xl,yl):
    fig = plt.figure(figsize=(4,3),dpi=200)
    ax = fig.add_subplot(111)
    ax.loglog(xs,ys,'o')
    ax.set_title(title)
    plt.xlabel(xl)
    plt.ylabel(yl)
    plt.show()

def main():
    master_bins = []
    master_corrs = []
    xs, ys, zs = load("./BoxOfGalaxies.csv")
    cubic_min = min(min(xs),min(ys),min(zs))
    cubic_max = max(max(xs),max(ys),max(zs))
    num_galax = len(xs)
    assert(len(xs) == len(ys) == len(zs))
    actual_galaxies = np.array(list(zip(xs,ys,zs)))
#    print("Planting trees, watering them, and letting them grow...")
#    actual_kd = space.cKDTree(actual_galaxies,3)
    print("Filling pool...")
    pool=Pool(processes=NUM_PROCESSORS)
    start=time.time()
    for x in range(5):
        print("Run {}:".format(x+1))
        print("    Generating random data set and corresponding tree...")
        random_galaxies = np.random.uniform(cubic_min,cubic_max,(num_galax,3))
#        random_kd = space.cKDTree(random_galaxies,3)
        bins = [(x*.1) + 1 for x in range(100)]
        random.shuffle(bins)
        print("    Computing correlation function...")
        print("    ",end="",flush=True)
        dr = 0.05
        
        correlation_func_of_r = list(pool.starmap(hamest,list(zip(bins,
                                                                   itertools.repeat(dr),
                                                                   itertools.repeat(actual_galaxies),
                                                                   itertools.repeat(random_galaxies)))))
        
        print("Complete.")
        master_bins.append(bins)
        master_corrs.append(correlation_func_of_r)
    print("Complete.")
    print("Operation took approximately {:.2f} seconds.".format(time.time()-start))
    writecsv(master_bins,master_corrs)
    #makeplot(bins,correlation_func_of_r,"Correlation function of distance r","Distance(Mpc/h)","correlation")

def writecsv(xslist,yslist):
    assert(len(xslist)==len(yslist))
    with open("./out.csv",'w') as csv:
        for row in range(len(xslist[0])):
            line = ""
            for cell in range(len(xslist)):
                line = line + str(xslist[cell][row]) + ',' + str(yslist[cell][row])+ ','
            line = line + '\n'
            csv.write(line)
if __name__ == "__main__":
    main()
"""
print("Generating plots...")
fig=plt.figure(figsize=(16,9), dpi=400)
ax = fig.add_subplot(111, projection='hammer')
ax.scatter(thetas, phis, s=mag, color = 'r', marker = '.', linewidth = "1")
ax.set_title('Angular Distribution of Galaxies')
plt.xlabel('azimuth')
plt.ylabel('elevation')
#ax2 = fig.add_subplot(212)
#numbins = 50
#ax2.hist(rho,numbins,color='g',alpha=0.8)

fig2=plt.figure(figsize=(15,5), dpi=400)
hs = fig2.add_subplot(131)
hs2= fig2.add_subplot(132)
hs3= fig2.add_subplot(133)
numbins = 50
hs.hist (xs,numbins,color='g',alpha=0.8)
hs2.hist(ys,numbins,color='g',alpha=0.8)
hs3.hist(zs,numbins,color='g',alpha=0.8)
hs.set_title ('Distribution of Galaxies by X position')
hs2.set_title('Distribution of Galaxies by Y position')
hs3.set_title('Distribution of Galaxies by Z position')
    
#ax = fig.add_subplot(131, projection='hammer')
#ax.scatter(thetas, phis, c='r', marker = 'o')

#ax2 = fig.add_subplot(132, projection='3d')
#ax2.scatter(xs, ys, zs, c='r', marker = 'o')

#ax3 = fig.add_subplot(133)
#ax3.scatter(phis, thetas, c = 'r', marker = 'o')

#plt.show()
print("Saving plots...")
with pdfback.PdfPages('out.pdf') as pdf:    
    pdf.savefig(fig)
    pdf.savefig(fig2)

print("Done!")
"""
