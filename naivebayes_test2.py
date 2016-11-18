# Bruce Maxwell
# Spring 2015
# CS 251 Project 8
#
# Naive Bayes class test
#

import sys
import data
import classifiers

def main(argv):

    if len(argv) < 3:
        print 'Usage: python %s <train data file> <test data file> <optional train categories> <optional test categories>' % (argv[0])
        exit(-1)

    dtrain = data.Data(argv[1])
    dtest = data.Data(argv[2])

    if len(argv) > 3:
        traincatdata = data.Data(argv[3])
        traincats = traincatdata.getDataNum( [traincatdata.getHeaderRaw()[0]] )
        testcatdata = data.Data(argv[4])
        testcats = testcatdata.getDataNum( [testcatdata.getHeaderRaw()[0]] )
        A = dtrain.getDataNum( dtrain.getHeaderRaw() )
        B = dtest.getDataNum( dtest.getHeaderRaw() )

    else:
        # assume the categories are the last column
        traincats = dtrain.getDataNum( [dtrain.getHeaderRaw()[-1]] )
        testcats = dtest.getDataNum( [dtest.getHeaderRaw()[-1]] )
        A = dtrain.getDataNum( dtrain.getHeaderRaw()[:-1] )
        B = dtest.getDataNum( dtest.getHeaderRaw()[:-1] )


    # create a new classifier
    nbc = classifiers.NaiveBayes()

    # build the classifier using the training data
    nbc.build( A, traincats )

    # use the classifier on the training data
    ctraincats, ctrainlabels = nbc.classify( A )
    ctestcats, ctestlabels = nbc.classify( B )

    print 'Results on Training Set:'
    print '     True  Est'
    for i in range(ctraincats.shape[0]):
        if int(traincats[i,0]) == int(ctraincats[i,0]):
            print "%03d: %4d %4d" % (i, int(traincats[i,0]), int(ctraincats[i,0]) )
        else:
            print "%03d: %4d %4d **" % (i, int(traincats[i,0]), int(ctraincats[i,0]) )

    print 'Results on Test Set:'
    print '     True  Est'
    for i in range(ctestcats.shape[0]):
        if int(testcats[i,0]) == int(ctestcats[i,0]):
            print "%03d: %4d %4d" % (i, int(testcats[i,0]), int(ctestcats[i,0]) )
        else:
            print "%03d: %4d %4d **" % (i, int(testcats[i,0]), int(ctestcats[i,0]) )
    return

if __name__ == "__main__":
    main(sys.argv)
