import sys
import data
import classifiers
from tabulate import tabulate


# Write a python function, probably in a new file, that does the following.
def main(argv):
    # Reads in a training set and its category labels, possibly as a separate file.

    # usage
    if len(argv)< 3:
        print "usage: python %s <Training File> <Test File> <opt: Training Categories> <opt: Test Categories> <KNN or NaiveBayes>" % (argv[0])
        return

    # read the training and test sets
    print "Reading: \n  Training: %s\n  Test: %s\n  KNN/NB: %s\n  " % (argv[1], argv[2], argv[-1])

    trainData = data.Data(argv[1])
    testData = data.Data(argv[2]) #test data

    headerList = [1,2]
    headerList[0] = trainData.getHeaderRaw()
    headerList[1] = testData.getHeaderRaw()

    # print trainData
    # print testData

    headers = [] #header names for cmtx


    # get the categories and the training data A and the test data B
    if len(argv) > 4:
        traincatdata = data.Data(argv[3])
        testcatdata = data.Data(argv[4])

        # needs to be a list
        traincats = traincatdata.getDataNum( [traincatdata.getHeaderRaw()[0]] )
        testcats = testcatdata.getDataNum( [testcatdata.getHeaderRaw()[0]] )

        A = trainData.getDataNum( trainData.getHeaderRaw() )
        B = testData.getDataNum( testData.getHeaderRaw() )
    else:

        # assume the categories are the last columnlen

        traincats = trainData.getDataNum( [trainData.getHeaderRaw()[-1]] )
        testcats = testData.getDataNum( [testData.getHeaderRaw()[-1]] )
        A = trainData.getDataNum( trainData.getHeaderRaw()[:-1] )
        B = testData.getDataNum( testData.getHeaderRaw()[:-1] )

    if argv[-1] == "NaiveBayes":
        classifier = classifiers.NaiveBayes()
    else:
        classifier = classifiers.KNN()

    classifier.build( A, traincats)
    ctraincats, ctrainlabels = classifier.classify( A )



    # print ctrainlabels[:20]
    # #
    # print traincats[:20]

    print "Training Data"
    print tabulate(classifier.confusionMatrixStr(classifier.confusionMatrix(traincats, ctrainlabels), headerList[0]))

    trainData.addCol("codes", "numeric", traincats.T.tolist()[0])
    #print "data: ", trainData.getDataNum(["Training Cats"])
    f = open('datasets/trainData.csv', 'w')
    trainData.writeOut(f, trainData.getHeaderRaw(), "numeric")
    print "\n"

    classifier.confusionMatrixGraphic(classifier.confusionMatrix(traincats, ctrainlabels), headerList[0], title = "Confusion Matrix of Training Data")

    print "Test Data"
    ctestcats, ctestlabels = classifier.classify( B )
    print tabulate(classifier.confusionMatrixStr(classifier.confusionMatrix(testcats, ctestlabels), headerList[1]))

    testData.addCol("Test Cats", "numeric", testcats.T.tolist()[0])
    #print "data: ", testData.getDataNum(["Training Cats"])
    f = open('datasets/testData.csv', 'w')
    testData.writeOut(f, testData.getHeaderRaw(), "numeric")
    print "\n"

    classifier.confusionMatrixGraphic(classifier.confusionMatrix(testcats, ctestlabels), headerList[1], title = "Confusion Matrix of Test Data")





if __name__ == "__main__":
    main(sys.argv)

    # Builds a classifier using the training set.
    # Classifies the training set and prints out a confusion matrix.
    # Classifies the test set and prints out a confusion matrix.
    # Writes out a new CSV data file with the test set data and the categories as an extra column. Your application should be able to read this file and plot it with the categories as colors.
