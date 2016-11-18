# Template by Bruce Maxwell
# Spring 2015
# CS 251 Project 8
#
# Classifier class and child definitions
import data
import analysis as an
import numpy as np
import numpy.matlib as matlib
import math
from scipy.spatial import distance as dist
from sklearn.metrics import confusion_matrix
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
from tabulate import tabulate
from copy import deepcopy



class Classifier:

    def __init__(self, type):
        '''The parent Classifier class stores only a single field: the type of
        the classifier.  A string makes the most sense.

        '''
        print "hi"
        self._type = type

    def type(self, newtype = None):
        '''Set or get the type with this function'''
        if newtype != None:
            self.type = newtype
        return self.type

    def confusionMatrix( self, truecats, classcats ):
        '''Takes in two Nx1 matrices of zero-index numeric categories and
        computes the confusion matrix. The rows represent true
        categories, and the columns represent the classifier output.

        '''
        unique, mapping = np.unique(np.array(truecats.T),return_inverse= True)
        #unique_class, mapping_class = np.unique(np.array(classcats.T), return_inverse=True)

        print unique

        cmtx = np.matlib.zeros((len(unique), len(unique)))

        for i in range(truecats.shape[0]):
            cmtx[int(mapping[i]), int(classcats[i, 0])] += 1

        print "unique: ", len(unique)
        print cmtx
        #return cmtx
        # print len(truecats)
        # print len(classcats)

        cmtx = confusion_matrix(truecats, classcats)

        # print cmtx
        return cmtx

    def confusionMatrixStr( self, cmtx, headers ):
        '''Takes in a confusion matrix and returns a string suitable for printing.'''
        # print "Length: %s, Width: %s" % (cmtx.shape[0], cmtx.shape[1])
        # print len(headers)
        cmtx = cmtx.astype(int).tolist() #convert to integer list

        table = []
        #headers = headers[:len(cmtx)]
        topHeaders = deepcopy(headers)
        topHeaders.insert(0, "Actual ->")
        table.append(topHeaders)
        for i, each in enumerate(cmtx):
            #print "i: %s" % (i)
            each.insert(0, headers[i])
            table.append(each)
        #print tabulate(table)
        return table

    def confusionMatrixGraphic(self, cmtx, headers, title = None):
        normal = []
        for i in cmtx:
            a = 0
            temp = []
            a = sum(i, 0)
            for j in i:
                temp.append(float(j)/float(a))
            normal.append(temp)

        fig = plt.figure()
        fig.canvas.set_window_title('Confusion Matrix')
        plt.clf()
        ax = fig.add_subplot(111)
        ax.set_aspect(1)
        res = ax.imshow(np.array(normal), cmap=plt.cm.jet, interpolation='nearest')

        for x in xrange(cmtx.shape[0]):
            for y in xrange(cmtx.shape[1]):
                ax.annotate(str(cmtx[x][y]), xy=(y, x),
                            horizontalalignment='center',
                            verticalalignment='center')

        cb = fig.colorbar(res)
        if title == None:
            plt.title('Confusion matrix of the classifier')
        else:
            plt.title(title)
        plt.xticks(range(cmtx.shape[0]), headers)
        plt.yticks(range(cmtx.shape[1]), headers)
        plt.show()
        return

    def __str__(self):
        '''Converts a classifier object to a string.  Prints out the type.'''
        return str(self.type)



class NaiveBayes(Classifier):
    '''NaiveBayes implements a simple NaiveBayes classifier using a
    Gaussian distribution as the pdf.

    '''

    def __init__(self, dataObj=None, headers=[], categories=None):
        print "hi"
        '''Takes in a Data object with N points, a set of F headers, and a
        matrix of categories, one category label for each data point.'''

        # call the parent init with the type
        Classifier.__init__(self, 'Naive Bayes Classifier')

        # store the headers used for classification
        self.headers = headers

        #self.numFeatures = len(headers)  # number of features

        self.numClasses = 0  # number of classes
        self.labels = []  # original class labels

        # unique data for the Naive Bayes: means, variances, scales
        self.means = []
        self.vars = []
        self.scales = []

        if dataObj != None:
            A = dataObj.getDataNum(self.headers)
            self.build(A, categories)


    def build( self, A, categories):
        '''Builds the classifier give the data points in A and the categories'''

        # figure out how many categories there are and get the mapping (np.unique)
        #print "Categories: ", categories
        unique, mapping = np.unique(np.array(categories.T), return_inverse=True)

        self.labels = unique

        #print A.shape
        #print type(A)

        self.numClasses = len(unique)

        self.categories = categories

        #print "mapping: ", mapping

        for i in range(self.numClasses):
            self.means.append(np.mean(A[(mapping == i), :], axis=0).tolist()[0])
            self.vars.append(np.var(A[(mapping == i), :], axis=0).tolist()[0])

        # create the matrices for the means, vars, and scales
        self.means = np.matrix(self.means) # mean(x)|c
        self.vars = np.matrix(self.vars) # |s(2/c)
        self.scales = 1 / np.sqrt(2 * math.pi * self.vars) # 1/root(2pi*s(|2/c))

        return

    def classify( self, A, return_likelihoods=False ):
        '''Classify each row of A into one category. Return a matrix of
        category IDs in the range [0..C-1], and an array of class
        labels using the original label values. If return_likelihoods
        is True, it also returns the NxC likelihood matrix.

        '''

        # error check to see if A has the same number of columns as
        # the class means
        assert self.means.shape[1] == A.shape[1]


        # make a matrix that is N x C to store the probability of each
        # class for each data point
        P = matlib.zeros((A.shape[0], self.numClasses)) # a matrix of zeros that is N (rows of A) x C (number of classes)

        # calculate the probabilities by looping over the classes
        #  with numpy-fu you can do this in one line inside a for loop

        for i in range(self.numClasses):
            P[:, i] = np.prod(np.multiply(self.scales[i, :], np.exp( -1 * np.square(A - self.means[i, :]) / (2 * self.vars[i, :]))), axis=1)

        #print "P: ", P

        # calculate the most likely class for each data point
        cats = np.argmax(P, axis=1)  # take the argmax of P along axis 1

        #print "Cats: ", cats
        # use the class ID as a lookup to generate the original labels
        #print "Labels: ", self.labels

        labels = self.labels[cats]

        if return_likelihoods:
            return cats, labels, P

        return cats, labels

    def __str__(self):
        '''Make a pretty string that prints out the classifier information.'''
        s = "\nNaive Bayes Classifier\n"
        for i in range(self.numClasses):
            s += 'Class %d --------------------\n' % (i)
            s += 'Mean  : ' + str(self.means[i,:]) + "\n"
            s += 'Var   : ' + str(self.vars[i,:]) + "\n"
            s += 'Scales: ' + str(self.scales[i,:]) + "\n"

        s += "\n"
        return s

    def write(self, filename):
        '''Writes the Bayes classifier to a file.'''
        # extension
        return

    def read(self, filename):
        '''Reads in the Bayes classifier from the file'''
        # extension
        return


class KNN(Classifier):

    def __init__(self, dataObj=None, headers=[], categories=None, K=None):
        '''Take in a Data object with N points, a set of F headers, and a
        matrix of categories, with one category label for each data point.'''

        # call the parent init with the type
        Classifier.__init__(self, 'KNN Classifier')

        # store the headers used for classification
        self.headers = headers
        # number of classes and number of features
        self.numClasses = 0
        self.numFeatures = 0

        # original class labels
        self.labels = []

        # unique data for the KNN classifier: list of exemplars (matrices)
        self.exemplars = []
        if dataObj != None:
            A = dataObj.getDataNum(headers)
            self.build(A, categories, K)

    def build( self, A, categories, K = None ):
        '''Builds the classifier give the data points in A and the categories'''

        # figure out how many categories there are and get the mapping (np.unique)
        unique, mapping = np.unique(np.array(categories.T), return_inverse=True)

        self.numClasses = len(unique)
        self.numFeatures = A.shape[1]
        self.labels = unique

        for i in range(self.numClasses):
            exemplar = A[(mapping == i), :]

            if K == None:
                # append to exemplars a matrix with all of the rows of A where the category/mapping is i
                self.exemplars.append(exemplar)
            elif K != None:
                print ""

                codebook = an.kmeansInit(exemplar, K)

                (codebook, codes, errors) = an.kmeansAlgorithm(exemplar, codebook) # run K-means on the rows of A where the category/mapping is i
                # print codebook.shape, "codebook", "ith codebook", i, K, "cluster"
                self.exemplars.append(codebook)  # append the codebook to the exemplars

        #self.write("KNN_classifier.csv")

        return

    def classify(self, A, K=3, return_distances=False):
        '''Classify each row of A into one category. Return a matrix of
        category IDs in the range [0..C-1], and an array of class
        labels using the original label values. If return_distances is
        True, it also returns the NxC distance matrix.

        The parameter K specifies how many neighbors to use in the
        distance computation. The default is three.'''

        # error check to see if A has the same number of columns as the class means
        if A.shape[1] != self.numFeatures:
            print "YO! dimensions are wrong: ", A.shape[1], self.numFeatures
            return


        # make a matrix that is N x C to store the distance to each class for each data point
        D = matlib.zeros((A.shape[0], self.numClasses))  # a matrix of zeros that is N (rows of A) x C (number of classes)

        for i in range(self.numClasses):
            # make a temporary matrix that is N x M where M is the number of exemplars (rows in exemplars[i])

            temp = np.matrix(dist.cdist(A, self.exemplars[i], 'euclidean'))

            temp = np.sort(temp,axis =1) # sort temp along columns

            D[:,i] = np.sum(temp[:,:K], axis =1) # sum the first K columns, this is the distance to the first class



        # calculate the most likely class for each data point
        cats = np.argmin(D,axis=1)  # take the argmin of D along axis 1


        # use the class ID as a lookup to generate the original labels
        labels = self.labels[cats]

        if return_distances:
            return cats, labels, D

        return cats, labels

    def __str__(self):
        '''Make a pretty string that prints out the classifier information.'''
        s = "\nKNN Classifier\n"
        for i in range(self.numClasses):
            s += 'Class %d --------------------\n' % (i)
            s += 'Number of Exemplars: %d\n' % (self.exemplars[i].shape[0])
            s += 'Mean of Exemplars  :' + str(np.mean(self.exemplars[i], axis=0)) + "\n"

        s += "\n"
        return s


    def write(self, filename):
        '''Writes the KNN classifier to a file.'''
        # extension
        return

    def read(self, filename):
        '''Reads in the KNN classifier from the file'''
        # extension
        return

#Classifier.confusionMatrixGraphic()
