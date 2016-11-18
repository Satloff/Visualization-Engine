# Theo Satloff
# Based on a file from Bruce A. Maxwell
# Spring 2015
#
# Executes PCA on the UCI activity recognition data set
# Identifies the # of eigenvectors required to represent at least 90% of the variation
# Clusters the projected data into 6 categories using the specified number of eigenvectors
# Classifies the data set
# Compares the classifications to actual classes using a confusion matrix
#
#
import sys
import data
import analysis as an
import numpy as np

def main(argv):

    if len(argv) < 3:
        print 'usage: python %s <Train CSV file> <Train categories CSV file>' % (argv[0])
        exit(-1)

    # read the features and categories data sets
    print 'Reading %s and %s' % (argv[1], argv[2])
    try:
        d = data.Data(argv[1])
    except:
        print 'Unable to open %s' % (argv[1])
        exit(-1)


    try:
        catdata = data.Data(argv[2])
    except:
        print 'Unable to open %s' % (argv[2])
        exit(-1)


    # execute PCA analysis
    print 'Executing PCA'
    pcadata = an.pca( d.getHeaderRaw(), d )

    print 'Evaluating eigenvalues'
    # identify how many dimensions it takes to represent 90% of the variation
    evals = pcadata.getEigenvalues()
    esum = np.sum(evals)
    cum = evals[0]
    cumper = cum / esum
    i = 1
    while cumper < .999:
        cum += evals[i]
        cumper = cum/esum
        i += 1

    print 'Dimensions to reach 99.9% of variation:', i

    cheaders = pcadata.getHeaderRaw()[:i]

    # cluster the data
    K = 6

    # Use the average of each category as the initial means
    truecats = catdata.getDataNum(catdata.getHeaderRaw()[0:1])
    tmpcats = truecats - 1

    print "categoroties:", #tmpcats.tolist()

    print 'Clustering to %d clusters' % (K)
    # print pcadata
    # print cheaders
    # print K
    codebook, codes, errors = an.kmeans(pcadata, cheaders, K, categories = tmpcats)

    print len(codes)
    print codebook

    # build a confusion matrix
    confmtx = [[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0]]

    codes = codes.astype(int)
    truecats = truecats.astype(int)

    print len(codes)
    print len(truecats)

    for i in range(codes.shape[0]):
        confmtx[codes[i,0]][int(truecats[i,0])-1] += 1

    print "\nConfusion Matrix:\n"
    print 'Actual->     Walking   Walk-up   Walk-dwn  Sitting   Standing   Laying'
    for i in range(len(confmtx)):
        s = 'Cluster %d' % (i)
        for val in confmtx[i]:
            s += "%10d" % (val)
        print s
    print

if __name__ == "__main__":
    main(sys.argv)
