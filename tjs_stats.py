import numpy as np


y_inputs = [27,16,11,4,3,1,6,9,18,25]
x_inputs = [[1,1,1,1,1,1,1,1,1,1],[-5,-4,-3,-2,-1,1,2,3,4,5],[2,0,2,0,2,0,2,0,2,0],[25,16,9,4,1,1,4,9,16,25]]

X = np.matrix(x_inputs).T # transposed so they are matrices
y = np.matrix(y_inputs).T


print
print "--------------- First Set -----------"
print


print "Look at the matrices to see if they look right"
print
print "X is: "
print X
print X.I

print "y is: "
print y
print X.T * X
#otherBeta = y * (X.I)
betaHat = (X.T * X).I * X.T * y
print "Betas:",(betaHat)
#print otherBeta


print
print "--------------- Second Set -----------"
print

new_set = [25,16,9,4,1,1,4,9,16,25]
x_inputs = x_inputs+[new_set]

X = np.matrix(x_inputs).T # transposed so they are matrices
y = np.matrix(y_inputs).T


betaHat = (X.T * X).I * X.T * y
print "Betas:",(betaHat)
