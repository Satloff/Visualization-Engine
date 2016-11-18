# Bruce A. Maxwell
# Spring 2015
# CS 251 Project 6
#
# PCA test function
#
import numpy as np
import data
import analysis
import sys

if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     print 'Usage: python %s <data file>' % (sys.argv[0])
    #     exit()

    d = data.Data( "datasets/pcatest.csv" )
    pcadata = analysis.pca( d.getHeaderRaw(), d, False )

    print "\nOriginal Data Headers"
    print pcadata.getDataHeaders()[2:]
    print "\nOriginal Data",
    print d.getDataNum( d.getHeaderRaw() )
    print "\nOriginal Data Means"
    print pcadata.getDataMeans()
    print "\nEigenvalues"
    print pcadata.getEigenvalues()
    print "\nEigenvectors"
    print pcadata.getEigenvectors()
    print "\nProjected Data"
    print pcadata.getDataNum(pcadata.getHeaderRaw())
