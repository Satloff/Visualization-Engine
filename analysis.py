# Theo Satloff
# spring 2016
# analyze data and return processed values

import data
import numpy as np
from scipy import stats
import PCAData
import clusterData
import scipy.cluster.vq as vq
from scipy.spatial.distance import pdist
from scipy.spatial import distance as dist
import random
import sys
import classifiers
from tabulate import tabulate
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt

debug = False

#---------return min and max of each column---------#
def dataRange(colHeaders, d):
	try:
		values = []
		for each in d.getDataNum(colHeaders).T.tolist():  # get every column, transpose them, convert to list form
			values.append([min(each), max(each)])

		if debug:
			print values
		return values
	except:
		print "please provide a valid header list"

#---------return the mean value of each column---------#
def mean(colHeaders, d):
	try:
		values = []
		for each in d.getDataNum(colHeaders).T.tolist():  # get every column, transpose them, convert to list form
			values.append(np.mean(each))

		if debug:
			print values
		return values
	except:
		print "please provide a valid header list"

#---------return the standard deviation of each column---------#
def stDev(colHeaders, d):
	try:
		values = []
		for each in d.getDataNum(colHeaders).T.tolist():  # get every column, transpose them, convert to list form
			values.append(np.std(each, ddof=1)) # delta degrees of freedom = 1, this way answers match with excel

		if debug:
			print values
		return values
	except:
		print "please provide a valid header list"

#---------normalize separate vector data---------#
def clusterNormalizeColSeparate(colHeaders, d):  # Bruce helped in explaining this type of normalization
	A = d.getDataNum(colHeaders)
	minA = np.min(A, axis=0)
	maxA = np.max(A, axis=0)
	diff = A - minA
	norm = diff/(maxA - minA)
	return norm

#---------normalize separate vector data---------#
def normalizeColSeparate(colHeaders, d):  # Bruce helped in explaining this type of normalization

	values = []
	final = []
	#print colHeaders
	for header in colHeaders:
		normalized = []
		temp = []
		for each in range(d.getNumRowNum()):
			#print "each", each
			#print "header", header
			temp.append(d.getValueNum(each, header))

		for x in temp:
			try:
				zi = (x-min(temp))/(max(temp)-min(temp))
			except:
				zi = 0
			normalized.append(zi)

		final.append(normalized)
	final = np.array( final ).T


	if debug:
		print final
	return final

#---------normalize a matrix---------#
def normalizeColTogether(colHeaders, d): # Bruce helped in explaining this type of normalization
	try:
		values = []
		for each in d.getDataNum(colHeaders).T.tolist():  # get every column, transpose them, convert to list form
			values.append(each)

		x = np.array(values)
		normalized = ((x-x.min())/(x.max()-x.min())).T

		if debug:
			print normalized
		return normalized
	except:
		print "please provide a valid header list"

#---------correlate (for now) two vectors---------#
def correlate(colHeaders, d):
	columns = d.getDataNum(colHeaders).T.tolist() # get every column, transpose them, convert to list form
	#print np.correlate(columns[0], columns[1])
	return np.corrcoef(columns[0:2])[0,1] # correlate each combination (ab, ac, bc, etc). For now, only correlate first two columns

def linear_regression(ind, dep, d):
	y = d.getDataNum([dep])
	A = d.getDataNum(ind)
	A = np.insert(A, 0, values=1, axis=1)
	AAinv = np.linalg.inv( np.dot(A.T, A))
	x = np.linalg.lstsq( A, y )
	b = x[0]
	N = len(y)
	C = len(b)
	df_e = N-C
	df_r = C-1
	error = y - np.dot(A, b)
	sse = np.dot(error.T, error)/ df_e
	stderr = np.sqrt(np.diagonal(sse[0,0] * AAinv))
	t = b.T / stderr
	p = 2*(1 - stats.t.cdf(abs(t), df_e))
	r2 = 1-error.var()/y.var()
	b0 = b[0,0]
	b = b[1:]

	return (b0, b, sse, r2, t, p)

# This version uses SVD
def pca(headers, d, normalize=True):
	if normalize:
		A = clusterNormalizeColSeparate(headers, d)
	else:
		A = d.getDataNum(headers)

	m = np.mean(A, axis=0)[0]
	m = np.array(m)
	M = m*np.ones( A.shape ) # this is so the mean is setup as the same dimensions as A

	D = A - M # difference between matrix A and m
	U, S, V = np.linalg.svd(D, full_matrices=False) #V = Evecs, S/(N-1) = Evals
	pdata = np.dot(V, D.T).T
	return PCAData.PCAData(headers, pdata, (S*S)/(d.getNumRowNum()-1), V, m)

def cluster(headers, d, K, means, codes, errors, normalize=True):
	if normalize:
		A = clusterNormalizeColSeparate(headers, d)
	else:
		A = d.getDataNum(headers)

	return clusterData.ClusterData(A, headers, K, means, codes, errors)
	#return PCAData.PCAData(headers, d, (S*S)/(d.getNumRowNum()-1), V, m)


def kmeansNumpy(d, headers, K, whiten = True):

	# assign to A the result of getting the data from your Data object
	A = d.getDataNum(headers)

	# assign to W the result of calling vq.whiten on A
	W = vq.whiten(A)

	# assign to codebook, bookerror the result of calling vq.kmeans with W and K
	codebook, bookerror = vq.kmeans(W,K)

	# assign to codes, error the result of calling vq.vq with W and the codebook
	codes,error = vq.vq(W,codebook)

	# return codebook, codes, and error
	return [codebook,codes,error]

def kmeansInit(A, K, categories = None):

	if categories == None:
		# print "A: ", A.shape[0]
		# print "K: ", K
		randomMeans = random.sample(range(1, A.shape[0]), K) # get random sample of K length from the size of A columns (without replacement)
		return A[randomMeans,:]

	# CITE: heavily borrowed from Vivek Sah's wiki post
	elif categories != None:
		maxval = categories.max() #get the max val in the categories// could be K-value-1
		Kdata = []
		for i in range(int(maxval)+1):
			rowList = np.where(categories== i)[0] #list of rows where i is an element
			partdata = A[rowList.tolist(),:] #get the corresponding rows from data
			krow = np.mean(partdata,axis=0) #get the mean of those rows
			Kdata.append(krow.tolist()) #append it to kmeans_list whcih will be converted to matrix
			# print Kdata
		return np.matrix(Kdata)

def kmeansClassify(A, means, distType = "euclidean"):

	codesErrors = []
	for i in range(A.shape[0]):
		d = [0, sys.maxint] #check it against all means, and store the row index of mean with distance with mean
		for j in range(means.shape[0]): #calculate distance metrics other than euclidean

			if distType == "euclidean":
				newd = dist.euclidean(A[i,:], means[j,:])
			elif  distType == "cosine":
				newd = dist.cosine(A[i,:], means[j,:])
			elif distType == "canberra":
				newd = dist.canberra(A[i,:], means[j,:])
			elif distType == "manhattan":
				newd = dist.cityblock(A[i,:], means[j,:])
			elif distType == "correlation":
				newd = dist.correlation(A[i,:], means[j,:])
			elif distType == "hamming":
				newd = dist.hamming(A[i,:], means[j,:])


			if newd < d[1]:
				d = [j, newd]

		codesErrors.append(d)

	return (np.matrix(codesErrors)[:,0], np.matrix(codesErrors)[:,1])  #returns the codes and errors

def kmeansAlgorithm(A, means, distType = "euclidean", threshold = 1e-7, iterations = 100):
	# set up some useful constants
	MIN_CHANGE = threshold
	MAX_ITERATIONS = iterations
	D = means.shape[1]
	K = means.shape[0]
	N = A.shape[0]

	# iterate no more than MAX_ITERATIONS
	for i in range(MAX_ITERATIONS):
		# calculate the codes
		codes, errors = kmeansClassify( A, means )

		# calculate the new means
		newmeans = np.zeros_like( means )
		counts = np.zeros( (K, 1) )
		for j in range(N):
			newmeans[int(codes[j,0]),:] += A[j,:]
			counts[int(codes[j,0]),0] += 1.0

		# finish calculating the means, taking into account possible zero counts
		for j in range(K):
			if counts[j,0] > 0.0:
				newmeans[j,:] /= counts[j, 0]
			else:
				newmeans[j,:] = A[random.randint(0,A.shape[0]),:]

		# test if the change is small enough
		diff = np.sum(np.square(means - newmeans))
		means = newmeans
		if diff < MIN_CHANGE:
			break

	# call classify with the final means
	codes, errors = kmeansClassify( A, means, distType )

	# return the means, codes, and errors
	return means, codes, errors


def kmeans(d, headers, K, whiten=True, categories = None, distType = "euclidean", threshold = 1e-7, iterations = 100):

	if K > 0 :
		 # assign to A the result getting the data given the headers
		A = d.getDataNum(headers)

		if whiten:

		  # assign to W the result of calling vq.whiten on the data
		  W = vq.whiten(A)
		else:
		  # assign to W the matrix A
		  W = A

		# assign to codebook the result of calling kmeansInit with W, K, and categories
		codebook = kmeansInit(W, K, categories)

		# assign to codebook, codes, errors, the result of calling kmeansAlgorithm with W and codebook
		(codebook,codes,errors) = kmeansAlgorithm(W, codebook, distType, threshold, iterations)

		# return the codebook, codes, and representation error
		return codebook, codes, errors

	else:

		print "analysis.py: kmeans() parameter problems"
def training(argv):
	# Reads in a training set and its category labels, possibly as a separate file.

	# read the training and test sets
	#print "Reading: \n  Training: %s\n  Test: %s\n  KNN/NB: %s\n  " % (argv[1], argv[2], argv[-1])

	trainData = data.Data(argv[0])
	testData = data.Data(argv[1]) #test data

	headerList = [1,2]
	headerList[0] = trainData.getHeaderRaw()
	headerList[1] = testData.getHeaderRaw()

	# print trainData
	# print testData

	headers = [] #header names for cmtx


	# get the categories and the training data A and the test data B
	if len(argv) > 4:
		traincatdata = data.Data(argv[2])
		testcatdata = data.Data(argv[3])

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

	print "this may take a little while..."

	classifier.build( A, traincats)
	ctraincats, ctrainlabels = classifier.classify( A )
	ctestcats, ctestlabels = classifier.classify( B )
	#print tabulate(classifier.confusionMatrixStr(classifier.confusionMatrix(testcats, ctestlabels), headerList[1]))

	trainDataStr = classifier.confusionMatrix(traincats, ctrainlabels)
	testDataStr = classifier.confusionMatrix(testcats, ctestlabels)

	print "done training"

	return trainDataStr, testDataStr, traincats.T.tolist()[0], testcats.T.tolist()[0], trainData, testData
	# print ctrainlabels[:20]
	# #
	# print traincats[:20]

	# print "Training Data"
	# print tabulate(classifier.confusionMatrixStr(classifier.confusionMatrix(traincats, ctrainlabels), headerList[0]))
	#
	# trainData.addCol("codes", "numeric", traincats.T.tolist()[0])
	# #print "data: ", trainData.getDataNum(["Training Cats"])
	# f = open('datasets/trainData.csv', 'w')
	# trainData.writeOut(f, trainData.getHeaderRaw(), "numeric")
	# print "\n"
	#
	# classifier.confusionMatrixGraphic(classifier.confusionMatrix(traincats, ctrainlabels), headerList[0], title = "Confusion Matrix of Training Data")
	#
	# print "Test Data"
	# ctestcats, ctestlabels = classifier.classify( B )
	# print tabulate(classifier.confusionMatrixStr(classifier.confusionMatrix(testcats, ctestlabels), headerList[1]))
	#
	# testData.addCol("Test Cats", "numeric", testcats.T.tolist()[0])
	# #print "data: ", testData.getDataNum(["Training Cats"])
	# f = open('datasets/testData.csv', 'w')
	# testData.writeOut(f, testData.getHeaderRaw(), "numeric")
	# print "\n"
	#
	# classifier.confusionMatrixGraphic(classifier.confusionMatrix(testcats, ctestlabels), headerList[1], title = "Confusion Matrix of Test Data")

	# return

def confusionMatrixGraphic(cmtx, headers, title = None):
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

def test():
	d = data.Data("datasets/pcatest.csv", "data2.csv")
	#colHeaders = ["a", "b", "c"]
	#print "dataRange(colHeaders, d): ", dataRange(colHeaders, d)
	#print "mean(colHeaders, d): ", mean(d.getHeaderNum())
	#print "stDev(colHeaders, d): ", stDev(colHeaders, d)
	#print "normalizeColSeparate(colHeaders, d): ", normalizeColSeparate(colHeaders, d)
	#print "normalizeColTogether(colHeaders, d): ", normalizeColTogether(colHeaders, d)
	#print "pca(): ", pca(colHeaders, d)
	#print "correlate(colHeaders, d): ", correlate(colHeaders, d)
	#print linear_regression(["X0"], "Y", d)

	#means = np.matrix( [[0.0,0.1], [0.95,1.0]] )



#test()
