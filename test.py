# Stephanie Taylor
# Spring 2014
# Test the Data class's ability to store and return information about data
#
#--------------
# Theo Satloff
# spring 2016
#

import sys
import data
import analysis as a
from tabulate import tabulate
import time

def testDataRaw():

	print "\n########################## testDataRow() ##########################\n"
	print "\n Testing the fields and acessors for raw data\n"
	d = data.Data("datasets/data.csv", "data2.csv")
	headers = d.getHeaderRaw()
	print "d.getHeadersRaw(): ", d.getHeaderRaw()
	print "d.getTypesRaw(): ", d.getTypesRaw()
	print "d.getNumColRaw(): ", d.getNumColRaw()
	print "d.getNumRowRaw(): ", d.getNumRowRaw()
	print "d.getRowRaw(0): ", d.getRowRaw(0)
	print "type( d.getRowRaw(0) ): ", type( d.getRowRaw(1) )
	print "d.getValueRaw(0,headers(0)): ", d.getValueRaw(0,'A')
	print "type(d.getValueRaw(0,headers(0))): ", type(d.getValueRaw(0,'A'))

	#d.addCol('Test Header','string', ['1', '2', '3', '4', '5', '6', '7', '8'])
	try:
		print "d.getValueRaw(7,'Test Header'): ", d.getValueRaw(7,'C')
		print "d.headers[9]: ", d.headers[9]
		print "d.type[9]: ", d.type[8]
	except:
		print "not enough rows"

	#print d.enum
	#ordered = sorted(d.enum, key=d.enum.__getitem__)
	#print ordered
	#d.addCol('Enum Timestamp','int', ordered)
	#print d.enum
	print "\n table of raw data with added column\n"
	print tabulate(d.data, headers = d.headers)
	d.writeOut() # you'll see that the new column was correctly written
	print "\n#####################################################################\n"

def testDataNum():
	print "\n########################## testDataNum() ##########################\n"
	print "\n Testing the fields and acessors for numerical data\n"
	d = data.Data("datasets/data.csv", "data2.csv")
	headers = d.getHeaderNum()
	print "d.getHeadersNum(): ", d.getHeaderNum()
	print "d.getNumColNum(): ", d.getNumColNum()
	print "d.getNumRowNum(): ", d.getNumRowNum()
	print "d.getRowNum(0): ", d.getRowNum(0)
	print "type( d.getRowNum(0) ): ", type( d.getRowNum(1) )
	#print "d.getValueNum(7, 'Alcohol'): ", d.getValueNum(7,'Alcohol')
	print "type(d.getValueNum(0,headers(0))): ", type(d.getValueNum(0,headers[0]))

	d.addCol('Test Header','numeric', [10, 20, 30, 40, 50, 60, 70, 80])
	print "d.getHeadersNum(): ", d.getHeaderNum()
	#print "d.getValueNum(7, 'Test Header'): ", d.getValueNum(7,'Test Header')
	#print "d.matrixData: \n", d.matrixData
	print "\n table of numeric data with added column\n"
	print tabulate(d.matrixData.tolist(), headers = d.getOrderedHeaderNum())

	d.writeOut() # you'll see that the new column was correctly written
	print "\n#####################################################################\n"

def testAdd():
	print "\n########################## testAdd() ##########################\n"
	d = data.Data("drugdeaths.xlsx", "data2.csv")
	print "d.getHeaderRaw(): ",d.getHeaderRaw()
	d.addCol('Test Header','string', ['1', '2', '3', '4', '5', '6', '7', '8'])
	print "d.getHeaderRaw() With add:",d.getHeaderRaw()
	#print d.data
	#print d.header2raw
	#print d.matrixData.tolist()
	val = d.header2matrix["Alcohol"]
	print "d.matrixData[1, d.header2matrix[\"Alcohol\"]]: ",d.matrixData[1, val]
	print "d.getNumRowNum(): ",d.getNumRowNum()
	print "\n table of data with added column\n"
	print tabulate(d.data, headers = d.headers)
	#print d.getDataNum(2, 5, ["Alcohol","Heroin", "Fentanyl"])
	print "\n#####################################################################\n"

def testAnalysis():
	print "\n########################## testAnalysis() ##########################\n"
	d = data.Data("drugdeaths.csv", "data2.csv")
	colHeaders = ["Heroin", "Prescription Opioid", "Alcohol", "Cocaine"]
	print "dataRange(colHeaders, d): ", a.dataRange(colHeaders, d)
	print "mean(colHeaders, d): ", a.mean(colHeaders, d)
	print "stDev(colHeaders, d): ", a.stDev(colHeaders, d)
	#print "normalizeColSeparate(colHeaders, d): ", a.normalizeColSeparate(colHeaders, d)
	#print "normalizeColTogether(colHeaders, d): \n", a.normalizeColTogether(colHeaders, d)
	#print colHeaders
	print "\n Normalization of individual columns\n"
	print tabulate(a.normalizeColSeparate(colHeaders, d).tolist(), headers = colHeaders)
	print "\n Normalization of entire matrix\n"
	print tabulate(a.normalizeColTogether(colHeaders, d).tolist(), headers = colHeaders)
	print "correlate(colHeaders, d): ", a.correlate(colHeaders, d)
	print "\n#####################################################################\n"

def buildPoints(headerList):
	d = data.Data("datasets/data.csv", "data2.csv")
	#self.clearData()
	print d.getNumRowNum()
	print len(headerList)
	if len(headerList) <= 2:
		zList = []
		hList = []
		for each in range(d.getNumRowNum()):
			zList.append(0)
			hList.append(1)
		d.addCol('Z','numeric', zList)
		d.addCol('H','numeric', hList)
	elif len(headerList) == 3:
		hList = []
		for each in range(d.getNumRowNum()):
			hList.append(1)
		print hList
		d.addCol('H','numeric', hList)

	print "d.getHeadersNum(): ", d.getHeaderNum()

	points = d.getDataNum(d.getHeaderRaw())
	print "matrix"
	print d.header2raw
	print d.header2matrix
	print "getData"
	print points

	print a.normalizeColTogether(headerList[:-1], d)

if __name__ == '__main__':
	#testDataRaw()
	#testDataNum()
	buildPoints(['A','B','C'])
	#testAdd()
	#testAnalysis()
