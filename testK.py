# Bruce A. Maxwell
# Spring 2015
# CS 251 Project 7
#
# Test file for kmeans_numpy function
# Expected output is below
#
# Codebook
#
# [[ 4.059737    4.08785958]
#  [ 2.03991735  2.06976598]]
#
# Codes
#
# [1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0]


import sys
import data
import analysis as an

def main():

    d = data.Data( "datasets/clusterdata.csv" )

    codebook, codes, errors = an.kmeansNumpy( d, d.getHeaderNum(), 2 )

    print "\nCodebook\n"
    print codebook

    print "\nCodes\n"
    print codes

if __name__ == "__main__":
    main()
