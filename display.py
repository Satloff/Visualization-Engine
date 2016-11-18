# Skeleton Tk interface example
# Written by Bruce Maxwell
# Modified by Stephanie Taylor
#
# CS 251
# Spring 2015
#
#-------------------------------
#
# Theo Satloff
# Feb 15th, 2016
# http://patorjk.com/software/taag/#p=display&f=Banner3&t=

import Tkinter as tk
import tkFont as tkf
import tkSimpleDialog
import tkFileDialog
import tkMessageBox
import ttk
import math
import random
import os
import getpass
import view
import data
import time
import analysis as a
import numpy as np
from scipy import stats
from copy import deepcopy
from operator import xor
from tabulate import tabulate
import colorsys
import csv
#import training
#import scipy.stats


debug = False


########  ####  ######  ########  ##          ###    ##    ##
##     ##  ##  ##    ## ##     ## ##         ## ##    ##  ##
##     ##  ##  ##       ##     ## ##        ##   ##    ####
##     ##  ##   ######  ########  ##       ##     ##    ##
##     ##  ##        ## ##        ##       #########    ##
##     ##  ##  ##    ## ##        ##       ##     ##    ##
########  ####  ######  ##        ######## ##     ##    ##

# create a class to build and manage the display
class DisplayApp:

	def __init__(self, width, height):

		self.clusterData = None

		self.naiveData = None

		self.curRotationX = 0
		self.curRotationY = 0


		self.fontColor = "#b2b6b9"
		self.frameColor = "#1f1f1f"
		self.backgroundColor = "#161616"
		self.textBoxColor = '#303030'

		self.regressionResults = None

		self.files = {}

		self.pointSize = None

		self.linReg = []
		self.regEnd = None

		# create a tk object, which is the root window
		self.root = tk.Tk()
		self.root.configure(background='#161616')

		#----- Declare Variables ----#
		# width and height of the window
		self.initDx = width
		self.initDy = height

		self.buildPointShape = "Circle"

		# set up the application state
		self.objects = [] # list of data objects that will be drawn in the canvas
		self.data = None # will hold the raw data someday.
		self.baseClick = None # used to keep track of mouse movement

		self.axesSelectX = 0
		self.axesSelectY = 0
		self.axesSelectZ = 0
		#-----------------------------#

		# set up the geometry for the window
		self.root.geometry( "%dx%d+50+30" % (self.initDx, self.initDy) )

		# set the title of the window
		self.root.title(eval("'Hi %s, have fun using M.I. A.D.V.I.S.O.R.!' % (getpass.getuser())"))

		# set the maximum size of the window for resizing
		self.root.maxsize( 1600, 900 )

		# setup the menus
		self.buildMenus()

		# build the controls
		self.buildControls()

		# build the Canvas
		self.buildCanvas()

		# bring the window to the front
		self.root.lift()

		# - do idle events here to get actual canvas size
		self.root.update_idletasks()

		# set up the key bindings
		self.setBindings()

		#----- Create View Object based on screen size ----#
		height = (self.canvas.winfo_screenheight()/2)-80
		width = (self.canvas.winfo_screenwidth()/2)-80
		shorter = min(height, width)
		self.view = view.View(height = shorter, width = shorter)
		#--------------------------------------------------#


		#----- Set Endpoints ----#
		origin = [0, 0, 0, 1]
		self.axesEndpoints = np.matrix( [origin, [1, 0, 0, 1], origin, [0, 1, 0, 1], origin, [0, 0, 1, 1]])
		self.axes = []
		#------------------------#

		self.buildAxes()


		if debug:
			print "from display.py (DisplayApp init)"
			print "Original Screen width = ",width," height = ",height,"\n"

			print "from display.py (DisplayApp init)"
			print "Modified Screen width = ",width," height = ",height,"\n"

			print "from display.py"
			print "axes (showing points in rows):"
			print self.axes

			print "axes transposed (showing points in columns):"
			print self.axesEndpoints.T


	##     ## ######## ##    ## ##     ##
	###   ### ##       ###   ## ##     ##
	#### #### ##       ####  ## ##     ##
	## ### ## ######   ## ## ## ##     ##
	##     ## ##       ##  #### ##     ##
	##     ## ##       ##   ### ##     ##
	##     ## ######## ##    ##  #######

	def buildMenus(self):

		#---- Declare Menu Object ----#
		# create a new menu object
		self.menu = tk.Menu(self.root)

		# set the root menu to our new menu
		self.root.config(menu = self.menu)

		# create a variable to hold the individual menus
		menulist = []

		# create a file menu
		filemenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "File", menu = filemenu )
		menulist.append(filemenu)

		# create commands menu
		cmdmenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "Command", menu = cmdmenu )
		menulist.append(cmdmenu)

		# create pca menu
		pcamenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "PCA", menu = pcamenu )
		menulist.append(pcamenu)

		# create cluster menu
		clustermenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "Cluster", menu = clustermenu )
		menulist.append(clustermenu)

		# create learning menu
		trainingmenu = tk.Menu( self.menu )
		self.menu.add_cascade( label = "Training", menu = trainingmenu )
		menulist.append(trainingmenu)

		self.linearBool = tk.BooleanVar()

		#---- Menu Text ----#
		# first sublist is file menu, second is commands menu
		menutext = [ 	["-",
					'Clear		\xE2\x8C\x98N',
					'Open		\xE2\x8C\x98O',
					'Quit			\xE2\x8C\x98Q'],
					['Linear Regression 	\xE2\x8C\x98R',
					'Choose Axes 		\xE2\x8C\x98D',
					'Save 				\xE2\x8C\x98S' ],
					['PCA	',
					'PCA Data'],
					['Cluster',
					'Save'],
					['Training',
					'Test cmtx',
					'Train cmtx'] ]


		#---- Menu Functions ----#
		# first sublist is file menu, second is commands menu
		menucmd = [ [None,
					self.handleClearData,
					self.handleOpen,
					self.handleQuit],
					[self.handleLinearRegression,
					self.handleDialog,
					self.saveRegression],
					[self.handlePCA,
					self.handleDisplayPCA],
					[self.handleCluster,
					self.saveCluster],
					[self.handleLearning,
					self.handleTestGraph,
					self.handleTrainGraph] ]


		#---- Build Menu ----#
		# build the menu elements and callbacks
		for i in range( len( menulist ) ):
			for j in range( len( menutext[i]) ):
				if menutext[i][j].partition(' ')[0] == 'Linear': # if the value is linear, make it a checkbox menu item
					menulist[i].add_checkbutton( label=menutext[i][j], onvalue=True, offvalue=0, variable=self.linearBool, command=self.handleLinearRegression)
				elif menutext[i][j] != '-':
					menulist[i].add_command( label = menutext[i][j], command=menucmd[i][j] )
				else:
					menulist[i].add_separator()


	########  #### ##    ## ########  #### ##    ##  ######    ######
	##     ##  ##  ###   ## ##     ##  ##  ###   ## ##    ##  ##    ##
	##     ##  ##  ####  ## ##     ##  ##  ####  ## ##        ##
	########   ##  ## ## ## ##     ##  ##  ## ## ## ##   ####  ######
	##     ##  ##  ##  #### ##     ##  ##  ##  #### ##    ##        ##
	##     ##  ##  ##   ### ##     ##  ##  ##   ### ##    ##  ##    ##
	########  #### ##    ## ########  #### ##    ##  ######    ######

	def setBindings(self):

		#---- Set bindings  ----#
		# bind mouse motions to the canvas
		self.canvas.bind( '<Button-1>', self.handleMouseButton1 )
		self.canvas.bind( '<B1-Motion>', self.handleMouseButton1Motion )

		self.canvas.bind( '<Button-2>', self.handleMouseButton2 )
		self.canvas.bind( '<Control-Button-1>', self.handleMouseButton2 )
		self.canvas.bind( '<B2-Motion>', self.handleMouseButton2Motion )
		self.canvas.bind( '<Control-B1-Motion>', self.handleMouseButton2Motion )

		self.canvas.bind( '<Button-3>', self.handleMouseButton3 )
		self.canvas.bind( '<Command-Button-1>', self.handleMouseButton3 )
		self.canvas.bind( '<B3-Motion>', self.handleMouseButton3Motion )
		self.canvas.bind( '<Command-B1-Motion>', self.handleMouseButton3Motion )

		self.canvas.bind( '<Shift-Control-Button-1>', self.handleDelete )

		# bind command sequences to the root window
		self.root.bind( '<Command-q>', self.handleQuit )
		self.root.bind( '<Command-n>', self.handleClearData )
		self.root.bind( '<Command-d>', self.handleDialog )
		self.root.bind( '<Command-r>', self.resetAxes )
		self.root.bind( '<Command-o>', self.handleOpen )
		self.root.bind( '<Command-s>', self.saveRegression )
		self.root.bind( '<Command-l>', self.handleLinearRegression)


	 ######     ###    ##    ## ##     ##    ###     ######
	##    ##   ## ##   ###   ## ##     ##   ## ##   ##    ##
	##        ##   ##  ####  ## ##     ##  ##   ##  ##
	##       ##     ## ## ## ## ##     ## ##     ##  ######
	##       ######### ##  ####  ##   ##  #########       ##
	##    ## ##     ## ##   ###   ## ##   ##     ## ##    ##
	 ######  ##     ## ##    ##    ###    ##     ##  ######

	# create the canvas object
	def buildCanvas(self):
		self.canvas = tk.Canvas( self.root, width=self.initDx, height=self.initDy, cursor = "pirate" )
		self.canvas.configure(background="#1f1f1f", highlightbackground="#161616" )
		self.canvas.pack( expand=tk.YES, fill=tk.BOTH )
		return


	 ######   #######  ##    ## ######## ########   #######  ##        ######
	##    ## ##     ## ###   ##    ##    ##     ## ##     ## ##       ##    ##
	##       ##     ## ####  ##    ##    ##     ## ##     ## ##       ##
	##       ##     ## ## ## ##    ##    ########  ##     ## ##        ######
	##       ##     ## ##  ####    ##    ##   ##   ##     ## ##             ##
	##    ## ##     ## ##   ###    ##    ##    ##  ##     ## ##       ##    ##
	 ######   #######  ##    ##    ##    ##     ##  #######  ########  ######

	# build a frame and put controls in it
	def buildControls(self):

		#---- Menu and Menu Item Declarations (ordered) ----#
		#---- Right Panel ----#
		# make a control frame on the right
		leftcntlframe = tk.Frame(self.root)
		leftcntlframe.configure(background=self.frameColor)
		leftcntlframe.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y) # draw the side frame

		#---- Separator for Right Panel ----#
		# make a separator frame
		sep = tk.Frame( self.root, height=self.initDy, width=2, bg = self.backgroundColor)
		sep.pack( side=tk.LEFT, padx = 2, pady = 2 ) # draw the side frame border

		#---- Axis Print Bottom ----#
		self.axisVals = tk.StringVar()
		#text = 'X: %s\nY: %s\nZ: %s' % ("---", "---","---")
		text = ""
		self.axisVals.set(text)

		axisLabel = tk.Label(leftcntlframe, textvariable = self.axisVals, fg = self.fontColor)
		axisLabel.configure(background=self.frameColor, justify='left')
		axisLabel.pack(side = tk.TOP)

		self.linRegInfo = tk.StringVar()
		text = ''
		self.linRegInfo.set(text)

		linRegInfoLabel = tk.Label(leftcntlframe, textvariable = self.linRegInfo, fg = self.fontColor)
		linRegInfoLabel.configure(background=self.frameColor, justify='left')
		linRegInfoLabel.pack(side = tk.TOP)

		#---- Right Panel ----#
		# make a control frame on the right
		rightcntlframe = tk.Frame(self.root)
		rightcntlframe.configure(background=self.frameColor)
		rightcntlframe.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y) # draw the side frame

		#---- Separator for Right Panel ----#
		# make a separator frame
		sep = tk.Frame( self.root, height=self.initDy, width=2, bg = self.backgroundColor)
		sep.pack( side=tk.RIGHT, padx = 2, pady = 2 ) # draw the side frame border

		#---- Top Label ----#
		# use a label to set the size of the right panel
		label = tk.Label( rightcntlframe, text="Control Panel", width=20, fg=self.fontColor )
		label.configure(background=self.frameColor)
		label.pack( side=tk.TOP, pady=10 )

		self.fileBox = tk.Listbox(rightcntlframe, selectmode=tk.SINGLE, exportselection=0, fg=self.fontColor)
		self.fileBox.configure(background=self.textBoxColor)
		for item in self.files: # declare shapes for possible data point creation
			self.fileBox.insert(tk.END, item)
		self.fileBox.pack(side = tk.TOP, pady=10)

		#---- Reset View Button ----#
		# when clicked, reset the 3D view
		resetButton = tk.Button( rightcntlframe, text="Reset View", command=self.resetAxes)
		resetButton.configure(highlightbackground=self.frameColor)
		resetButton.pack(side=tk.TOP)

		deleteFile = tk.Button( rightcntlframe, text="Delete", command=self.handleDeleteFile)
		deleteFile.configure(highlightbackground=self.frameColor)
		deleteFile.pack(side=tk.TOP)

		#---- Clear Data Button ----#
		# when clicked, reset the 3D view
		clear = tk.Button( rightcntlframe, text="Clear Data", command=self.handleClearData)
		clear.configure(highlightbackground=self.frameColor)
		clear.pack(side=tk.TOP)

		#---- Rotation Speed Label ----#
		label = tk.Label( rightcntlframe, text="Rotation Speed", width=20, fg=self.fontColor )
		label.configure(background=self.frameColor)
		label.pack( side=tk.TOP, pady=10 )

		#---- Rotation Speed Slider ----#
		self.rotationSpeed = tk.Scale(rightcntlframe, from_=1.0, to=20.0, fg = self.fontColor)
		self.rotationSpeed.configure(background=self.frameColor, highlightbackground=self.frameColor, orient=tk.HORIZONTAL)
		self.rotationSpeed.pack()

		#---- Transformation Speed Label ----#
		label = tk.Label( rightcntlframe, text="Transformation Speed", width=20, fg=self.fontColor )
		label.configure(background=self.frameColor)
		label.pack( side=tk.TOP, pady=10 )

		#---- Transformation Speed Slider ----#
		self.transformationSpeed = tk.Scale(rightcntlframe, from_=1.0, to=20.0, fg = self.fontColor)
		self.transformationSpeed.configure(background=self.frameColor, highlightbackground=self.frameColor, orient=tk.HORIZONTAL)
		self.transformationSpeed.pack()

		#---- Size slider Label ----#
		label = tk.Label( rightcntlframe, text="Choose Size", width=20, fg=self.fontColor )
		label.configure(background=self.frameColor)
		label.pack( side=tk.TOP, pady=10 )

		#---- Size Slider ----#
		self.sizeSlide = tk.Scale(rightcntlframe, from_=0, to=100, fg = self.fontColor, command = self.handleSizeSlide)
		self.sizeSlide.configure(background=self.frameColor, highlightbackground=self.frameColor, orient=tk.HORIZONTAL)
		self.sizeSlide.pack()

		#---- Color Label ----#
		label = tk.Label( rightcntlframe, text="Change Color", width=20, fg=self.fontColor )
		label.configure(background=self.frameColor)
		label.pack( side=tk.TOP, pady=10 )

		# make a menubutton
		self.colorOption = tk.StringVar( self.root )
		self.colorOption.set("pink")
		colorMenu = tk.OptionMenu( rightcntlframe, self.colorOption, "pink", "blue", "red", "green" ) # can add a command to the menu
		colorMenu.configure(bg=self.frameColor)
		colorMenu.pack(side=tk.TOP)

		#---- Update Color Button ----#
		# make a button in the frame
		# and tell it to call the handleButton method when it is pressed.
		button = tk.Button( rightcntlframe, text="Update Color", command=self.handleButton1 )
		button.configure(highlightbackground=self.frameColor)
		button.pack(side=tk.TOP)

		#---- Bottom Frame ----#
		# make a control frame on the bottom
		bottomframe = tk.Frame(self.root)
		bottomframe.configure(background=self.frameColor)

		bottomframe.pack(side=tk.BOTTOM, padx=2, pady=2, fill=tk.X)

		#---- Separator for Bottom ----#
		# make a separator frame
		sep = tk.Frame( self.root, width=self.initDx, height=2, bg=self.backgroundColor)
		sep.pack( side=tk.BOTTOM, padx = 2, pady = 2)

		#---- Angle Print Bottom ----#
		self.angle = tk.StringVar()
		text = 'Rotation: %s/%s' % ("---", "---")
		self.angle.set(text)

		angle1 = tk.Label(bottomframe, textvariable = self.angle, fg = self.fontColor)
		angle1.configure(background=self.frameColor)
		angle1.pack(side = tk.LEFT)

		#---- Zoom Print Bottom ----#
		self.zoom = tk.StringVar()
		text = '   Zoom: %s%%' % ("100")
		self.zoom.set(text)

		zoom1 = tk.Label(bottomframe, textvariable = self.zoom, fg = self.fontColor)
		zoom1.configure(background=self.frameColor)
		zoom1.pack(side = tk.LEFT)

		#---- Status Bar Bottom ----#
		self.status = tk.StringVar()
		text = '---'
		self.status.set(text)

		console = tk.Label(bottomframe, textvariable = self.status, fg = self.fontColor)
		console.configure(background=self.frameColor)
		console.pack(side = tk.RIGHT)

		#---- Bottom Frame ----#
		# make a control frame on the bottom
		bottomframe2 = tk.Frame(self.root)
		bottomframe2.configure(background=self.frameColor)

		bottomframe2.pack(side=tk.BOTTOM, padx=2, pady=2, fill=tk.X)

		#---- Separator for Bottom ----#
		# make a separator frame
		sep = tk.Frame( self.root, width=self.initDx, height=2, bg=self.backgroundColor)
		sep.pack( side=tk.BOTTOM, padx = 2, pady = 2)

		return

	########  ##     ## #### ##       ########        ###    ##     ## ########  ######
	##     ## ##     ##  ##  ##       ##     ##      ## ##    ##   ##  ##       ##    ##
	##     ## ##     ##  ##  ##       ##     ##     ##   ##    ## ##   ##       ##
	########  ##     ##  ##  ##       ##     ##    ##     ##    ###    ######    ######
	##     ## ##     ##  ##  ##       ##     ##    #########   ## ##   ##             ##
	##     ## ##     ##  ##  ##       ##     ##    ##     ##  ##   ##  ##       ##    ##
	########   #######  #### ######## ########     ##     ## ##     ## ########  ######

	def buildAxes(self):
		vtm = self.view.build()
		pts = (vtm * self.axesEndpoints.T).T

		if debug:
			print "from display.py"
			print "Multiplied and Re-transposed Points (in rows):"
			print pts

		#----- Add axes to axes list ------#
		self.axes.append(self.canvas.create_line(pts[0,0], pts[0,1], pts[1,0], pts[1,1], fill="#e95065", dash=(4, 4))) #dash=(4, 4)
		self.axes.append( self.canvas.create_line(pts[2,0], pts[2,1], pts[3,0], pts[3,1], fill="#2980b9", dash=(4, 4)))
		self.axes.append(self.canvas.create_line(pts[4,0], pts[4,1], pts[5,0], pts[5,1], fill="#52d97a", dash=(4, 4)))

		#----- create axes label objects ----#
		self.xlabel = self.canvas.create_text(pts[1,0], pts[1,1], text = "X", fill = self.fontColor)
		self.ylabel = self.canvas.create_text(pts[3,0], pts[3,1], text = "Y", fill = self.fontColor)
		self.zlabel = self.canvas.create_text(pts[5,0], pts[5,1], text = "Z", fill = self.fontColor)

		#----- create blank label objects for when headers are read in ----#
		self.xlabelText = self.canvas.create_text(pts[1,0], pts[1,1], text = "", fill = self.fontColor)
		self.ylabelText = self.canvas.create_text(pts[3,0], pts[3,1], text = "", fill = self.fontColor)
		self.zlabelText = self.canvas.create_text(pts[5,0], pts[5,1], text = "", fill = self.fontColor)

		if debug:
			print "x Axis = ",pts[0,0], pts[0,1], pts[1,0], pts[1,1]
			print "y Axis = ",pts[2,0], pts[2,1], pts[3,0], pts[3,1]
			print "z Axis = ",pts[4,0], pts[4,1], pts[5,0], pts[5,1]


	def handleDialog(self, event=None): # process dialog box for selecting axes
		#print self.d.getHeaderNum()
		self.handleFileList()
		print "D: ", self.d
		try:
			dialog = ChooseAxes(self.root, self.d, self.clusterData)
		except AttributeError:
			text = "No File Selected"
			self.status.set(text)
			print "No File Selected"
			return
		#print dialog.result
		if dialog.result == None:
			return

		(self.axesSelectX, self.axesSelectY, self.axesSelectZ, self.pointColor, self.pointSize, self.pointShape, self.borderColor, self.borderSize, self.clusterSmooth, self.clusterData) = dialog.result

		if self.clusterData != None: # if there are more clusters than colors, choose smooth colors
			try:
				value = int(self.d.getK()) # this doesnt make sense... hence the "why me lord"
			except:
				#print self.d.getDataNum([self.d.getHeaderRaw()[-1]]).T.tolist()[0]
				value = max(self.d.getDataNum([self.d.getHeaderRaw()[-1]]).T.tolist()[0])
				#print "Value: ", value
			if value > 11:
				self.clusterSmooth = 1

		self.pointHeaders = [self.axesSelectX, self.axesSelectY, self.axesSelectZ, self.pointColor, self.pointSize, self.borderColor, self.borderSize]

		text = ' X: %s\nY: %s\nZ: %s\nColor: %s\nSize: %s\nShape: %s\nB-Color: %s\nB-Size: %s' % (self.axesSelectX, self.axesSelectY, self.axesSelectZ, self.pointColor, self.pointSize, self.pointShape, self.borderColor, self.borderSize)
		self.axisVals.set(text)

		#text = 'X: %s\nY: %s\nZ: %s\n' % ("Hi", "BI", "---")
		#self.DataDisplay.axisVals.set(text)


		self.xAxisName = self.axesSelectX
		self.yAxisName = self.axesSelectY
		self.zAxisName = self.axesSelectZ

		self.handlePlotData()

	########  ########  ######  ######## ########
	##     ## ##       ##    ## ##          ##
	##     ## ##       ##       ##          ##
	########  ######    ######  ######      ##
	##   ##   ##             ## ##          ##
	##    ##  ##       ##    ## ##          ##
	##     ## ########  ######  ########    ##

	def resetAxes(self, event=None):
		height = (self.canvas.winfo_screenheight()/2)-80 # reset everything
		width = (self.canvas.winfo_screenwidth()/2)-80
		shorter = min(height, width)
		self.view = view.View(shorter, shorter)
		#self.axes
		self.updateAxes()
		if len(self.objects) > 0: # if points exist, reset those too
			self.updatePoints()
		if len(self.linReg) > 0: #only do this if the lin reg has been made
			self.updateFits()

		text = "View Reset"
		self.status.set(text)
		text = '   Zoom: %s%%' % ("100")
		self.zoom.set(text)
		print 'View Reset'

	##     ## ########  ########     ###    ######## ########
	##     ## ##     ## ##     ##   ## ##      ##    ##
	##     ## ##     ## ##     ##  ##   ##     ##    ##
	##     ## ########  ##     ## ##     ##    ##    ######
	##     ## ##        ##     ## #########    ##    ##
	##     ## ##        ##     ## ##     ##    ##    ##
	 #######  ##        ########  ##     ##    ##    ########

	def updateAxes(self): # based on Steph's function
		vtm = self.view.build()
		pts = (vtm * self.axesEndpoints.T).T

		#----- Edit the coordinate values of each line ----#
		self.canvas.coords(self.axes[0], pts[0,0], pts[0,1], pts[1,0], pts[1,1])
		self.canvas.coords(self.axes[1], pts[2,0], pts[2,1], pts[3,0], pts[3,1])
		self.canvas.coords(self.axes[2], pts[4,0], pts[4,1], pts[5,0], pts[5,1])

		#----- edit the coordinate values of the labels ----#
		self.canvas.coords(self.xlabel, pts[1,0], pts[1,1])
		self.canvas.coords(self.ylabel, pts[3,0], pts[3,1])
		self.canvas.coords(self.zlabel, pts[5,0], pts[5,1])


		if len(self.objects) > 0: # if points exist, update the text labels
			self.canvas.coords(self.xlabelText, (pts[0,0]+pts[1,0])/2, (pts[0,1]+pts[1,1])/2)
			self.canvas.itemconfigure(self.xlabelText, text = self.xAxisName)
			self.canvas.coords(self.ylabelText, (pts[2,0]+pts[3,0])/2, (pts[2,1]+pts[3,1])/2)
			self.canvas.itemconfigure(self.ylabelText, text = self.yAxisName)
			self.canvas.coords(self.zlabelText, (pts[4,0]+pts[5,0])/2, (pts[4,1]+pts[5,1])/2)
			self.canvas.itemconfigure(self.zlabelText, text = self.zAxisName)


	########  ##     ## #### ##       ########     ########   #######  #### ##    ## ########  ######
	##     ## ##     ##  ##  ##       ##     ##    ##     ## ##     ##  ##  ###   ##    ##    ##    ##
	##     ## ##     ##  ##  ##       ##     ##    ##     ## ##     ##  ##  ####  ##    ##    ##
	########  ##     ##  ##  ##       ##     ##    ########  ##     ##  ##  ## ## ##    ##     ######
	##     ## ##     ##  ##  ##       ##     ##    ##        ##     ##  ##  ##  ####    ##          ##
	##     ## ##     ##  ##  ##       ##     ##    ##        ##     ##  ##  ##   ###    ##    ##    ##
	########   #######  #### ######## ########     ##         #######  #### ##    ##    ##     ######


	def get_spaced_colors(self, n):
	    max_value = 16581375 #255**3
	    interval = int(max_value / n)
	    colors = [hex(I)[2:].zfill(6) for I in range(0, max_value, interval)]

	    return [(int(i[:2], 16), int(i[2:4], 16), int(i[4:], 16)) for i in colors]

	def buildPoints(self, headerList, d):
		# This is a written a sort of poorly. I'd like to go back and fix this when i have time
		# Techincal Debt :(

		xyz = headerList[0]
		headerList = headerList[1]
		#print "XYZ", xyz
		#print "Header", headerList

		self.clearData()

		#------- Messy Process for Organizing Plotting Data -------#
		if self.pointColor != None: # if point color was selected, normalize and multiply by 255
			norm = a.normalizeColSeparate(xyz, d)
			self.colorNorm = norm.T[0]*255
		if self.pointSize != None: # if point size was selected, normalize and multiply by max size (15)
			norm = a.normalizeColSeparate(headerList[1], d)
			self.sizeNorm = (norm.T[0]+1)*15
		if self.pointShape != None: # no point shape funcitonality yet.
			#a.normalizeColSeparate(headerList[1][2], d)
			print "shape is circle"
		if self.borderColor != None: # if border color was selected, normalize and multiply by 255
			norm = a.normalizeColSeparate(headerList[3], d)
			self.borderColorNorm = norm.T[0]*255
		if self.borderSize != None: # if border size was selected, normalize and multiply by max size 3
			norm = a.normalizeColSeparate(headerList[4], d)
			self.borderSizeNorm = (norm.T[0]+1)*3

		self.data = a.normalizeColSeparate(xyz, d) #normalize select headers (excluding 0 or 1)


		#------- Z is unselected, add values for matrices -------#
		if len(xyz) == 2: # if Z is unselected
			zList = []
			hList = []
			for each in range(d.getNumRowNum()): # for every row, add 0 and 1
				zList.append(0)
				hList.append(1)
			zList = np.array([zList])
			hList = np.array([hList])
			self.data = self.data.T
			self.data = np.append(self.data, zList, axis=0)
			self.data = np.append(self.data, hList, axis=0)
			self.data = self.data.T


		#------- Z is selected, add values for matrices -------#
		elif len(xyz) == 3: # if there are 3 rows
			hList = []
			for each in range(d.getNumRowNum()): # for every row, add 0 and 1
				hList.append(1)
			hList = np.array([hList])
			self.data = np.append(self.data.T, hList, axis=0)
			self.data = self.data.T

		self.points = d.getDataNum(d.getHeaderNum()) # return the columns of select headers

		#------- Cluster color list generator -------#
		#print "cluster: ", self.clusterData
		if self.clusterData != None:
			try:
				naiveData = self.d.getDataNum([self.d.getHeaderRaw()[-1]]).astype(int).T.tolist()[0]
				#print "data length: ", len(naiveData)
			except:
				print "idk... something went wrong"
			#print naiveData

			#print "second smooth: ",self.clusterSmooth
			if self.clusterSmooth == 1:
				#print "Smooth... oooooh yeah"
				try:
					N = max(self.d.getClusterId())+1
				except:
					N = max(naiveData)+1
				HSV_tuples = [(x*1.0/N, 0.5, 0.5) for x in range(N)]
				RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
				tk_rgb = []
				for each in RGB_tuples:
					color = (each[0]*255, each[1]*255, each[2]*255)
					tk_rgb.append("#%02x%02x%02x" % color)

				#print "rgb Length: ", len(tk_rgb)
			else:
				#print "rough... ouch"
				tk_rgb = ["#1abc9c", "#3498db", "#9b59b6", "#34495e", "#ecf0f1", "#e67e22", "#f39c12", "#95a5a6", "#27ae60", "#e74c3c", "#7f8c8d", "#2980b9"]


			#print self.d.getClusterId()
		vtm = self.view.build()
		pts = (vtm * self.data.T).T

		self.headerList = headerList

		#print "got here hi hi"
		if self.pointShape == "circle":
			for i, each in enumerate(pts): # create an oval at every point
				x = each[0,0]
				y = each[0,1]
				if len(headerList) >= 2:

					if self.clusterData == None:
						#------- continuation of Messy Process for Organizing Plotting Data -------#
						if self.pointColor != None: # assign color values depending on if value was assigned or not
							rgb = "#%02x%02x%02x" % (255-self.colorNorm[i], 255-self.colorNorm[i], 0+self.colorNorm[i])
						else:
							rgb = "#16a085"
					# elif self.naiveData != None:
					# 	ID = self.naiveData[i]
					# 	rgb = tk_rgb[ID]
					else:
						try:
							ID = self.d.getClusterId()[i]
						except:
							ID = naiveData[i]
						rgb = tk_rgb[ID]


					if self.pointSize != None: # if value was assigned, set size
						size = self.sizeNorm[i]
					else:
						size = 10
					if self.borderColor != None: # if value was assigned, set border color
						rgb2 = "#%02x%02x%02x" % (255-self.borderColorNorm[i], 0+self.borderColorNorm[i], 255-self.borderColorNorm[i])
					else:
						rgb2 = "#9f1616"
					if self.borderSize != None: # if value was assigned, set border width
						size2 = self.borderSizeNorm[i]
					else:
						size2 = 0

					self.objects.append(self.canvas.create_oval(x, y, x+size, y+size, fill = rgb, outline=rgb2, activefill = "#00ffcd", width=size2))
				else:
					self.objects.append(self.canvas.create_oval(x, y, x+10, y+10, fill = "#16a085", outline='', activefill = "#00ffcd"))

				#self.objectsData.append([])

		elif self.pointShape == "square": # this isnt used right now
			for i, each in enumerate(pts): # create an oval at every point
				x = each[0,0]
				y = each[0,1]
				self.objects.append(self.canvas.create_rectangle(x, y, x+self.sizeNorm[i], y+self.sizeNorm[i], fill = self.pointColor, outline=''))

	##     ## ########  ########     ###    ######## ########
	##     ## ##     ## ##     ##   ## ##      ##    ##
	##     ## ##     ## ##     ##  ##   ##     ##    ##
	##     ## ########  ##     ## ##     ##    ##    ######
	##     ## ##        ##     ## #########    ##    ##
	##     ## ##        ##     ## ##     ##    ##    ##
	 #######  ##        ########  ##     ##    ##    ########

	def updatePoints(self):
		vtm = self.view.build()
		pts = (vtm * self.data.T).T

		for i, each in enumerate(pts): #For every value, add new coordinates
			x = each[0,0]
			y = each[0,1]


			if len(self.headerList) >= 2:

				if self.pointSize != None: # if value is assigned, set size
					size = self.sizeNorm[i]
				else:
					size = 10

				self.canvas.coords(self.objects[i], x, y, x+size+self.sizeAdd, y+size+self.sizeAdd)
			else:
				self.canvas.coords(self.objects[i], x, y, x+10+self.sizeAdd, y+10+self.sizeAdd)

	def updateFits(self, event = None):
		if len(self.linReg) > 0:
			vtm = self.view.build()

			intercept, slope, sse, r2, t, p = a.linear_regression(self.headerList[:-1], self.headerList[-1], self.d)

			rangeXY = a.dataRange(self.headerList, self.d)

			x0 = 0.0
			x1 = 1.0
			y0 = ((rangeXY[0][0] * slope[0,0] + intercept) - rangeXY[1][0])/(rangeXY[1][1] - rangeXY[1][0])
			y1 = ((rangeXY[0][1] * slope[0,0] + intercept) - rangeXY[1][0])/(rangeXY[1][1] - rangeXY[1][0])

			if len(self.headerList) > 2:
				z0 = ((rangeXY[0][0] * slope[1,0] + intercept) - rangeXY[2][0])/(rangeXY[2][1] - rangeXY[2][0])
				z1 = ((rangeXY[0][1] * slope[1,0] + intercept) - rangeXY[2][0])/(rangeXY[2][1] - rangeXY[2][0])
			else:
				z0 = 0
				z1 = 0

			norm = np.array([[x0, y0, z0, 1], [x1, y1, z1, 1]])

			pts = (vtm * norm.T).T

			self.canvas.coords(self.linReg[0], pts[0,0], pts[0,1], pts[1,0], pts[1,1])

	def clearData(self, event=None): # clear just the points
		for obj in self.objects:
			self.canvas.delete(obj)	# delete every point in the self.objects list from the canvas
			self.objects = []

		for obj in self.linReg:
			self.canvas.delete(obj)
			self.linReg = []

		self.regressionResults = None

		self.linearBool.set(False)

		#self.clusterData = None



		text = 'Rotation: %s/%s' % ("---", "---")
		self.angle.set(text)

		#text = 'X: %s\nY: %s\nZ: %s\n\n' % ("---", "---", "---")
		text = ""
		self.axisVals.set(text)

		text = ''
		self.linRegInfo.set(text)

		text = "Cleared the screen"
		self.status.set(text)
		print 'Cleared the screen'
		return

	def clearLabel(self, event=None): # clear just the labels

		self.canvas.itemconfigure(self.xlabelText, text = "") # dont delete the object, but set text back to nothing
		self.canvas.itemconfigure(self.ylabelText, text = "")
		self.canvas.itemconfigure(self.zlabelText, text = "")

	def resetPointValues(self):
		self.pointColor = None
		self.pointSize = None
		self.pointShape = None
		self.borderColor = None
		self.borderSize = None

	def handleClearData(self, event=None): # clear everything
		self.clearData()
		self.clearLabel()
		self.clusterData = None

	def handlePlotData(self, event=None):
		# try: # check to see if self.d contains the data object
		headerList = [[self.pointColor], [self.pointSize], [self.pointShape], [self.borderColor], [self.borderSize]] #this is messy, but for normalization needs to be lists

		#self.buildPoints(headerList, self.d) # use the selection from dialog box for axes selection

		#print "data ", self.axesSelectX, self.axesSelectY


		if self.axesSelectZ == None:
			#print "got here too"
			self.buildPoints([[self.axesSelectX, self.axesSelectY], headerList], self.d) # use the selection from dialog box for axes selection
		else:
			#print "got here"
			print self.axesSelectX, self.axesSelectY, self.axesSelectZ
			print headerList
			#print "cluster Build: ", self.clusterData

			self.buildPoints([[self.axesSelectX, self.axesSelectY, self.axesSelectZ], headerList], self.d) # use the selection from dialog box for axes selection

		text = "Data Added!"
		self.status.set(text)
		print 'Data Added'
		#self.d = None
		self.updateAxes()

		# except AttributeError:
		# 	text = "No File Selected"
		# 	self.status.set(text)
		# 	print "No File Selected"

	def handleFileList(self):
		selection = self.fileBox.curselection()
		if selection:
			#self.handleClearData()
			self.clusterData = None

			result = self.fileBox.get(self.fileBox.curselection()[0])
			fn = self.files[result]
			if result.split('.')[-1] == "pca" or result.split('.')[-1] == "clu":
				self.d = fn
				if result.split('.')[-1] == "clu":
					self.clusterData = "not None"

				#print "If D:", self.d
			elif result.split('.')[-1] == "train":
				self.d = fn

			else:
				#print "fn: ", fn
				self.d = data.Data(fn, "data2.csv")
				#print self.d

	def handleDeleteFile(self):
		selection = self.fileBox.curselection()
		if selection:
			result = self.fileBox.get(selection[0])
			del self.files[result]
			self.fileBox.delete(selection[0]) # clear
			self.d = None

	def handleOpen(self, event=None):
		count = 0
		fn = tkFileDialog.askopenfilename( parent=self.root, title='Choose a data file', initialdir='.' )
		if fn.split('.')[-1] == "csv": # check that the file type is readable
			count = 1
		elif fn.split('.')[-1] == "xlsx":
			count = 1
		else: #if it isnt, print an error
			ftype = fn.split('.')[-1]
			text = "\"%s\" file type not allowed!" % (ftype)
			self.status.set(text)

			tkMessageBox.showwarning(eval("'\"%s\" file type not allowed!' % (ftype)"),eval("'%s... I cant convert \"%s\" file type to readable data.' % (getpass.getuser(), ftype)"))
			return
		self.files[fn.split('/')[-1]] = fn
		self.fileBox.insert(tk.END, fn.split('/')[-1])

		self.d = data.Data(fn, "data2.csv")
		text = "%s loaded!" % (fn.split('/')[-1])
		self.status.set(text)

		#self.handleDialog()

	def handleDelete(self, event=None):
		print ""

	def handleQuit(self, event=None):
		print 'Terminating'
		self.root.destroy()


	def getColor(self):
		color = askcolor()
		print color

	def handleSizeSlide(self, event=None):
		self.sizeAdd = self.sizeSlide.get()
		if len(self.objects) > 0: #only do this if the data has been read in
			self.updatePoints()

	########  ########  ######   ########  ########  ######   ######  ####  #######  ##    ##
	##     ## ##       ##    ##  ##     ## ##       ##    ## ##    ##  ##  ##     ## ###   ##
	##     ## ##       ##        ##     ## ##       ##       ##        ##  ##     ## ####  ##
	########  ######   ##   #### ########  ######    ######   ######   ##  ##     ## ## ## ##
	##   ##   ##       ##    ##  ##   ##   ##             ##       ##  ##  ##     ## ##  ####
	##    ##  ##       ##    ##  ##    ##  ##       ##    ## ##    ##  ##  ##     ## ##   ###
	##     ## ########  ######   ##     ## ########  ######   ######  ####  #######  ##    ##

	def buildLinearRegression(self, headerList, d):
		self.headerList = headerList
		cleanData = d.getDataNum(headerList) #un-normalized data
		print cleanData
		vtm = self.view.build()

		intercept, slope, sse, r2, t, p = a.linear_regression(headerList[:-1], headerList[-1], d) # find the linear regression of x values and a y

		self.regressionResults = intercept, slope, sse, r2, t, p

		rangeXY = a.dataRange(headerList, d)

		print "range", rangeXY
		print "slope", slope

		x0 = 0.0
		x1 = 1.0
		#((xmin * m + b) - ymin)/(ymax - ymin)
		#((xmax * m + b) - ymin)/(ymax - ymin)

		y0 = ((rangeXY[0][0] * slope[0,0] + intercept) - rangeXY[1][0])/(rangeXY[1][1] - rangeXY[1][0]) # find the y values of the regression line
		y1 = ((rangeXY[0][1] * slope[0,0] + intercept) - rangeXY[1][0])/(rangeXY[1][1] - rangeXY[1][0])

		if len(headerList) > 2:
			z0 = ((rangeXY[0][0] * slope[1,0] + intercept) - rangeXY[2][0])/(rangeXY[2][1] - rangeXY[2][0]) # if there is a second x, find the z values of regression line
			z1 = ((rangeXY[0][1] * slope[1,0] + intercept) - rangeXY[2][0])/(rangeXY[2][1] - rangeXY[2][0])
		else:
			z0 = 0
			z1 = 0

		norm = np.array([[x0, y0, z0, 1], [x1, y1, z1, 1]]) # make a matrix of 3D coordinate values
		#print norm

		pts = (vtm * norm.T).T

		self.linReg.append(self.canvas.create_line(pts[0,0], pts[0,1], pts[1,0], pts[1,1], fill="#e95065")) #plot the regression line

		final = ''
		for each in slope.tolist():
			string = str(each[0]) + "\n"
			final += string

		text = 'Slope: %s\nY-Int: %s\nR^2: %s' % (final, intercept, r2)
		self.linRegInfo.set(text)
		#print "Analysis: b0: %s, b: %s, sse: %s, r2: %s, t: %s, p: %s" % (a.linear_regression([headerList[0], headerList[1]], headerList[0], d))
		#print "hello:", a.linear_regression([headerList[0], headerList[1]], headerList[0], d)

	def saveRegression(self):
		if self.regressionResults == None:
			tkMessageBox.showwarning("Save Error!","Nothing to save.") # prompt error if regression doesnt exist
		else:
			intercept, slope, sse, r2, t, p = self.regressionResults # retrieve the regression information
			f = tkFileDialog.asksaveasfile(mode='w', defaultextension=".txt") # as where to save file, also ask for filename
			if f is None: #dialog closed with "cancel"
				return
			text2save = "Intercept: %s\nSlope: %s\nSSE: %s\nR2: %s\nT: %s\nP: %s" % (intercept, slope, sse, r2, t, p) #str(text.get(1.0, END)) # starts from `1.0`, not `0.0`
			f.write(text2save) # save the regression information to the filename provided
			f.close()

	def saveCluster(self):
		self.handleFileList() # get result of selecting from listbox

		if self.clusterData == None:
			tkMessageBox.showwarning("Save Error!","Nothing to save.") # prompt error if regression doesnt exist

		f = tkFileDialog.asksaveasfile(mode='w', defaultextension=".csv") # as where to save file, also ask for filename
		if f is None: #dialog closed with "cancel"
			return

		self.d.writeOut(f, self.d.getHeaderRaw())

		# data = self.d.getDataNum(self.d.getHeaderNum())
		# temp = []
		# temp.insert(0, self.d.getHeaderNum())
		#
		# for i in range(data.shape[0]):
		# 	temp.append(data[i,:].tolist()[0])
		#
		# writer = csv.writer(f)
		# writer.writerows(temp)

		text = "saved file"
		self.status.set(text)
		print "saved file"

	def save(self):
		if self.clusterData != None:
			self.handleFileList() # get result of selecting from listbox
			f = tkFileDialog.asksaveasfile(mode='w', defaultextension=".csv") # as where to save file, also ask for filename
			if f is None: #dialog closed with "cancel"
				return
			self.d.writeOut(f, self.d.getHeaderNum())

		elif self.regressionResults != None:
			intercept, slope, sse, r2, t, p = self.regressionResults # retrieve the regression information
			f = tkFileDialog.asksaveasfile(mode='w', defaultextension=".txt") # as where to save file, also ask for filename
			if f is None: #dialog closed with "cancel"
				return
			text2save = "Intercept: %s\nSlope: %s\nSSE: %s\nR2: %s\nT: %s\nP: %s" % (intercept, slope, sse, r2, t, p) #str(text.get(1.0, END)) # starts from `1.0`, not `0.0`
			f.write(text2save) # save the regression information to the filename provided
			f.close()


	def handleLinearRegression(self, event=None):

		try:
			test = self.d

		except:
			self.linearBool.set(False)
			text = "Axes not yet selected"
			self.status.set(text)
			print "Axes not yet selected"
			return

		if self.linearBool.get(): # if the boolean from menu is true, handle the linear regression
			if self.axesSelectZ is None:
				headerList = [self.axesSelectX, self.axesSelectY]
			else:
				headerList = [self.axesSelectX, self.axesSelectZ, self.axesSelectY]

			self.buildLinearRegression(headerList, self.d)

			self.updateAxes()
		else: # if the boolean from menu is false, clear the linear regression
			for obj in self.linReg:
				self.canvas.delete(obj)
				self.linReg = []

			self.regressionResults = None

			text = ''
			self.linRegInfo.set(text)


	def handlePCA(self):
		self.handleFileList() # get result of selecting from listbox

		try:
			dialog = ChoosePCA(self.root, self.d)
		except AttributeError:
			text = "No File Selected"
			self.status.set(text)
			print "No File Selected"
			return
		headers, name, self.PCAnormalize = dialog.result # ger results of the dialog box PCA

		pcad = a.pca( headers, self.d, self.PCAnormalize ) # make PCA object

		self.files[name] = pcad # save the PCA object
		self.fileBox.insert(tk.END, name)

		xyz = ['X', 'Y']
		headerList = [[None], [None], [None], [None], [None]]

		xyz[0] = headers[0]
		xyz[1] = headers[1]
		self.axesSelectX, self.axesSelectY = xyz
		try:
			xyz.append(headers[2])
			self.axesSelectZ = headers[2]
		except IndexError:
			self.axesSelectZ = None
		try:
			self.pointColor = headers[3]
		except IndexError:
			self.pointColor = None
		try:
			self.pointSize = headers[4]
		except IndexError:
			self.pointSize = None
		try:
			self.pointShape = headers[5]
		except IndexError:
			self.pointShape = None
		try:
			self.borderColor = headers[6]
		except IndexError:
			self.borderColor = None
		try:
			self.borderSize = headers[7]
		except IndexError:
			self.borderSize = None

		# for i, each in enumerate(xyz):
		# 	xyz[i] = pcad.header2header[each]
		#
		# for i, each in enumerate(headers):
		# 	xyz[i] = pcad.header2header[each]

		headerList = [[self.pointColor], [self.pointSize], [self.pointShape], [self.borderColor], [self.borderSize]]

	def handleDisplayPCA(self):

		self.handleFileList() #get result of listbox
		try:
			values = self.d.getEigenvalues()
			fHeaders = self.d.getHeaderRaw()
			headers = self.d.getOriginalHeaders()
			vectors = self.d.getEigenvectors()

			headers.insert(0, "e-vals") # add column header e-vals
			headers.insert(0, "e-vecs") # add column header e-vecs


			dialog = DisplayPCA(self.root, fHeaders, headers, values, vectors)
		except AttributeError:
			text = "No PCA Selected"
			self.status.set(text)
			print "No PCA Selected"
			return

	def handleCluster(self):
		self.handleFileList() # get result of selecting from listbox

		try:
			dialog = ChooseCluster(self.root, self.d)
		except AttributeError:
			text = "No File Selected"
			self.status.set(text)
			print "No File Selected"
			return

		try:
			headers, types, K, threshold, iterations = dialog.result # get results of the dialog box cluster
		except:
			text = "assignment error"
			self.status.set(text)
			print "assignment error"
			return

		text = "Made a cluster! (.clu)"
		self.status.set(text)
		print "Made a cluster! (.clu)"

		# print headers
		# print self.d.getHeaderRaw()

		#clusterMeans, clusterID, errors = a.kmeansNumpy(pcad, pcad.getHeaderRaw(), int(K))
		clusterMeans, clusterID, errors = a.kmeans(self.d, headers, int(K), distType = types, threshold = threshold, iterations = iterations)
		self.clusterData = "not None"

		# print clusterID.astype(int).T[0,0]
		# print np.array(clusterID.astype(int))

		clusterD = a.cluster(headers, self.d, K, clusterMeans, clusterID, errors)

		# print clusterD.getHeaderNum()
		# print clusterD.getMeans()
		# print clusterD.getClusterId()
		# print clusterD.getK()

		filename = time.strftime("%X")+".clu"
		self.files[filename] = clusterD # save the PCA object
		self.fileBox.insert(tk.END, filename)

		xyz = ['X', 'Y']
		headerList = [[None], [None], [None], [None], [None]]

		xyz[0] = headers[0]
		xyz[1] = headers[1]
		self.axesSelectX, self.axesSelectY = xyz
		try:
			xyz.append(headers[2])
			self.axesSelectZ = headers[2]
		except IndexError:
			self.axesSelectZ = None
		try:
			self.pointColor = headers[3]
		except IndexError:
			self.pointColor = None
		try:
			self.pointSize = headers[4]
		except IndexError:
			self.pointSize = None
		try:
			self.pointShape = headers[5]
		except IndexError:
			self.pointShape = None
		try:
			self.borderColor = headers[6]
		except IndexError:
			self.borderColor = None
		try:
			self.borderSize = headers[7]
		except IndexError:
			self.borderSize = None

		headerList = [[self.pointColor], [self.pointSize], [self.pointShape], [self.borderColor], [self.borderSize]]

	def handleLearning(self):

		self.handleFileList() #get result of listbox

		dialog = ChooseLearning(self.root)
		#self.trainDataFile, self.testDataFile, self.trainCatFile, self.testCatFile, self.machineType
		learningList = dialog.result
		self.trainDataStr, self.testDataStr, trainCats, testCats, trainData, testData = a.training(learningList)
		trainData.addCol("codes", "numeric", trainCats)

		print trainData

		self.files['trainData.train'] = trainData # save the PCA object
		self.fileBox.insert(tk.END, 'trainData.train')

		testData.addCol("codes", "numeric", testCats)
		print testData

		self.files['testData.train'] = testData # save the PCA object
		self.fileBox.insert(tk.END, 'testData.train')


	def handleTestGraph(self):
		try:
			a.confusionMatrixGraphic(self.trainDataStr, self.files['trainData.train'].getHeaderRaw(), title = "Confusion Matrix of Test Data")
		except:
			print "no test file"
			text = "No test file"
			self.status.set(text)

	def handleTrainGraph(self):
		try:
			a.confusionMatrixGraphic(self.testDataStr, self.files['testData.train'].getHeaderRaw(), title = "Confusion Matrix of Train Data")
		except:
			print "no train file"
			text = "No train file"
			self.status.set(text)


	########  ##     ## ######## ########  #######  ##    ##  ######
	##     ## ##     ##    ##       ##    ##     ## ###   ## ##    ##
	##     ## ##     ##    ##       ##    ##     ## ####  ## ##
	########  ##     ##    ##       ##    ##     ## ## ## ##  ######
	##     ## ##     ##    ##       ##    ##     ## ##  ####       ##
	##     ## ##     ##    ##       ##    ##     ## ##   ### ##    ##
	########   #######     ##       ##     #######  ##    ##  ######

	def handleButton1(self): # change color of objects
		for obj in self.objects:
			self.canvas.itemconfig(obj, fill=self.colorOption.get())

		print 'handling command button: ', self.colorOption.get()

	#Handle Shape Button
	def handleShape(self):
		selection=self.shapeBox.curselection()
		value = self.shapeBox.get(selection[0])

		self.buildPointShape = value

		print 'handling command button 3: ', value

	def handleMenuCmd1(self):
		print 'handling menu command 1'

	##     ##  #######  ##     ##  ######  ########
	###   ### ##     ## ##     ## ##    ## ##
	#### #### ##     ## ##     ## ##       ##
	## ### ## ##     ## ##     ##  ######  ######
	##     ## ##     ## ##     ##       ## ##
	##     ## ##     ## ##     ## ##    ## ##
	##     ##  #######   #######   ######  ########

	def handleMouseButton1(self, event):
		self.baseClick = (event.x, event.y) # record the coordinates of the mouse click
		self.transSpeed = float(self.transformationSpeed.get()) # record the speed set by the slider

		print 'handle mouse button 1: %d %d' % (event.x, event.y)

		foundMatch = False

		clickData = []
		for obj in self.objects:
			loc = self.canvas.coords(obj)
			if (loc[0] <= event.x <= loc[2] and loc[1] <= event.y <= loc[3]):

				item = self.canvas.find_withtag(obj)[0] # check to see if a point exists here
				#print item
				listItem = self.objects.index(item) # what position is this item in the object list?
				#print listItem

				if self.pointHeaders != None:
					for each in self.pointHeaders: # get the data from each point header read in
						try:
							clickData.append(self.d.getValueNum(listItem, each))
						except:
							text = "Processing error"
							self.status.set(text)

				elif self.linHeaders != None:
					for each in self.linHeaders:
						#print each
						clickData.append(self.d.getValueNum(listItem, each))

				color = self.canvas.itemcget(obj, "fill") # return the fill color

				foundMatch = True  # I could probably also interrupt this loop if a point has been found.

		if foundMatch:

			text = "Found a (%s) color point at %sx%s" % (color, event.x, event.y)
			self.status.set(text)

			if self.pointHeaders != None:
				text = 'X: %s\nY: %s\nZ: %s\nColor: %s\nSize: %s\nShape: %s\nB-Color: %s\nB-Size: %s\n' % (clickData[0], clickData[1], clickData[2], clickData[3], clickData[4], self.pointShape, clickData[5], clickData[6])

			elif self.linHeaders != None:
				text = 'X: %s\nY: %s\nZ: %s\nColor: %s\nSize: %s\nShape: %s\nB-Color: %s\nB-Size: %s\n' % (clickData[0], clickData[1], None, None, None, None, None, None)

			self.axisVals.set(text)


		else:
			text = "No point at %sx%s" % (event.x, event.y)
			self.status.set(text)

	#	print 'handle mouse button 1: %d %d' % (event.x, event.y)
	#	self.baseClick = (event.x, event.y)


	def handleMouseButton2(self, event):
		self.baseClick2 = (event.x, event.y) # record the coordinates of the mouse click 2
		self.viewOriginal = deepcopy(self.view) # make an unliked copy
		self.speed = float(self.rotationSpeed.get()) # record the speed set by the slider

		print 'handle mouse button 2: %d %d' % (event.x, event.y)

	def handleMouseButton3(self, event):
		self.baseClick = (event.x, event.y) # record the coordinates of the mouse click
		self.baseExtent = deepcopy(self.view.extent) #make an unlinked copy

		print 'handle mouse button 3: %d %d' % (event.x, event.y)

	# This is called if the first mouse button is being moved
	def handleMouseButton1Motion(self, event):
		# calculate the difference
		diff = ( event.x - self.baseClick[0], event.y - self.baseClick[1] )

		#text = 'X-Position: %s    Y-Position: %s' % (event.x, event.y) # print the x and y coordinates of the mouse motion in frame
		#self.mouse1coord.set(text)

		# Calculate the differential motion, divide it by the screen size. Take the hor and vert motion, and multiply by hor and vert extents
		dx= (float(event.x - self.baseClick[0])/self.view.screen[0])*self.view.extent[0,0]
		dy= (float(event.y - self.baseClick[1])/self.view.screen[1])*self.view.extent[0,1]

		# Put the result in delta0 and delta1
		delta0 = dx/self.transSpeed
		delta1 = dy/self.transSpeed

		# The VRP should be updated by delta0 * U + delta1 * VUP (this is a vector equation)
		self.view.vrp = self.view.vrp + delta0*self.view.u + delta1*self.view.vup

		self.updateAxes()

		if len(self.objects) > 0: #only do this if the data has been read in
			self.updatePoints()

		if len(self.linReg) > 0: #only do this if the lin reg has been made
			self.updateFits()

		self.baseClick = ( event.x, event.y )

	# This is called if the second button of a real mouse has been pressed
	# and the mouse is moving. Or if the control key is held down while
	# a person moves their finger on the track pad.
	def handleMouseButton2Motion(self, event):
		diff = ( event.x - self.baseClick2[0], event.y - self.baseClick2[1] )

		delta0 = (-diff[0])/(self.speed*self.view.screen[0])*math.pi # calculate the radian angle at which the axes should move
		delta1 = (diff[1])/(self.speed*self.view.screen[1])*math.pi

		self.curRotationX += delta0*(180/math.pi)  # turn radian into degrees
		self.curRotationY += delta1*(180/math.pi)  # this only shows how much the object has rotated on this click. it doesnt store previous data

		text = 'Rotation: %.3s/%.3s ' % (self.curRotationX, self.curRotationY)
		self.angle.set(text)

		self.view = deepcopy(self.viewOriginal) # set view to the value of the on click view
		self.view.rotateVRC(delta0, delta1) # pass VRC the radian values
		self.updateAxes()

		if len(self.objects) > 0:
			self.updatePoints()

		if len(self.linReg) > 0: #only do this if the lin reg has been made
			self.updateFits()

	def handleMouseButton3Motion(self, event): # help from Steph
		# calculate the difference
		dy = event.y - self.baseClick[1]
		k = 1.0/self.canvas.winfo_screenheight()
		f = 1.0 + k *dy # scale factor
		#print "f: ", f
		f = max(min(f, 3.0), 0.1)
		self.view.extent = self.baseExtent *  f
		self.updateAxes()
		if len(self.objects) > 0:
			self.updatePoints()
		if len(self.linReg) > 0: #only do this if the lin reg has been made
			self.updateFits()

		text = '   Zoom: %.5s%%' % (100+(100-self.view.extent[0,0]*100)) # there is probably a cleaner way to do this. it prints the zoom percentage
		self.zoom.set(text)


		#print 'handle button3 motion %d %d - new size: %d' % (diff[0], diff[1], self.randomDataPointSize)

	def main(self):
		print 'Calling randomDist routine'
		#self.handleDialog()
		print 'Entering main loop'
		self.root.mainloop()


########  ####    ###    ##        #######   ######       ######  ##          ###     ######   ######
##     ##  ##    ## ##   ##       ##     ## ##    ##     ##    ## ##         ## ##   ##    ## ##    ##
##     ##  ##   ##   ##  ##       ##     ## ##           ##       ##        ##   ##  ##       ##
##     ##  ##  ##     ## ##       ##     ## ##   ####    ##       ##       ##     ##  ######   ######
##     ##  ##  ######### ##       ##     ## ##    ##     ##       ##       #########       ##       ##
##     ##  ##  ##     ## ##       ##     ## ##    ##     ##    ## ##       ##     ## ##    ## ##    ##
########  #### ##     ## ########  #######   ######       ######  ######## ##     ##  ######   ######

class Dialog(tk.Toplevel):

	def __init__(self, parent, title = None):

		tk.Toplevel.__init__(self, parent)

		self.transient(parent)

		if title:
			self.title(title)

		self.parent = parent

		self.result = None

		body = tk.Frame(self)
		self.initial_focus = self.body(body)

		body.pack(padx=5, pady=5)

		self.buttonbox()

		self.grab_set()

		if not self.initial_focus:
			self.initial_focus = self

		self.protocol("WM_DELETE_WINDOW", self.cancel)

		self.geometry("+%d+%d" % (parent.winfo_rootx()+50, parent.winfo_rooty()+50))

		self.initial_focus.focus_set()

		self.wait_window(self)

	#
	# construction hooks

	def body(self, master):
		# create dialog body.  return widget that should have
		# initial focus.  this method should be overridden

		pass

	def buttonbox(self):
		# add standard button box. override if you don't want the
		# standard buttons

		box = tk.Frame(self)

		w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=tk.LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

		pass

	#
	# standard button semantics

	def ok(self, event=None):

		if not self.validate():
			self.initial_focus.focus_set() # put focus back
			return

		self.withdraw()
		self.update_idletasks()

		self.apply()

		self.cancel()

	def cancel(self, event=None):

		# put focus back to the parent window
		self.parent.focus_set()
		self.destroy()

	#
	# command hooks

	def validate(self):

		return 1 # override

	def apply(self):

		pass # override

########     ###    ##    ## ########   #######  ##     ##    ########  ####  ######  ########
##     ##   ## ##   ###   ## ##     ## ##     ## ###   ###    ##     ##  ##  ##    ##    ##
##     ##  ##   ##  ####  ## ##     ## ##     ## #### ####    ##     ##  ##  ##          ##
########  ##     ## ## ## ## ##     ## ##     ## ## ### ##    ##     ##  ##   ######     ##
##   ##   ######### ##  #### ##     ## ##     ## ##     ##    ##     ##  ##        ##    ##
##    ##  ##     ## ##   ### ##     ## ##     ## ##     ##    ##     ##  ##  ##    ##    ##
##     ## ##     ## ##    ## ########   #######  ##     ##    ########  ####  ######     ##

class randomDist(Dialog):
	def __init__(self, parent):
		Dialog.__init__(self, parent, "Distribution")

	def body(self, parent):
		# use a label to set the size of the right panel
		label = tk.Label( self, text="--X-Axis Distribution--", width=20 )
		label.pack( side=tk.TOP, pady=10 )

		self.listbox1 = tk.Listbox(self, selectmode=tk.SINGLE, exportselection=0)
		for item in ["Gaussian", "Uniform"]: # declare shapes for possible data point creation
			self.listbox1.insert(tk.END, item)
		self.listbox1.pack(side = tk.TOP)

		# use a label to set the size of the right panel
		label = tk.Label( self, text="--Y-Axis Distribution--", width=20 )
		label.pack( side=tk.TOP, pady=10 )

		self.listbox2 = tk.Listbox(self, selectmode=tk.SINGLE, exportselection=0)
		for item in ["Gaussian", "Uniform"]: # declare shapes for possible data point creation
			self.listbox2.insert(tk.END, item)
		self.listbox2.pack(side = tk.TOP)

		pass

	def apply(self):

		xAxis = self.listbox1.get(self.listbox1.curselection()[0])
		yAxis = self.listbox2.get(self.listbox2.curselection()[0])
		self.result = (xAxis, yAxis)

 ######  ##     ##  #######   #######   ######  ########       ###    ##     ## ########  ######
##    ## ##     ## ##     ## ##     ## ##    ## ##            ## ##    ##   ##  ##       ##    ##
##       ##     ## ##     ## ##     ## ##       ##           ##   ##    ## ##   ##       ##
##       ######### ##     ## ##     ##  ######  ######      ##     ##    ###    ######    ######
##       ##     ## ##     ## ##     ##       ## ##          #########   ## ##   ##             ##
##    ## ##     ## ##     ## ##     ## ##    ## ##          ##     ##  ##   ##  ##       ##    ##
 ######  ##     ##  #######   #######   ######  ########    ##     ## ##     ## ########  ######

class ChooseAxes(Dialog):
	def __init__(self, parent, d, clusterData):
		self.d = d
		self.clusterData = clusterData
		Dialog.__init__(self, parent, "Choose Axes")

	def body(self, parent):
		#print self.d.getHeaderNum() # test to see if everything eas passed correctly

		if self.d.getHeaderRaw()[-1] == "codes":
			self.clusterData = "not none"

		# use a label to set the size of the right panel
		#box = tk.Frame(self)
		frame0 = tk.Frame(self)
		frame0.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y) # draw the side frame

		frame1 = tk.Frame(self)
		frame1.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y) # draw the side frame

		self.frame2 = tk.Frame(self)
		self.frame2.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y) # draw the side frame

		self.frame3 = tk.Frame(self)
		self.frame3.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y) # draw the side frame

		self.frame4 = tk.Frame(self)
		self.frame4.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y) # draw the side frame

		label = tk.Label( frame0, text="X-Axis (X0)", width=20 )
		label.pack( side=tk.TOP, pady=10 )

		self.xAxisBox = tk.Listbox(frame0, selectmode=tk.SINGLE, exportselection=0)
		for item in self.d.getHeaderNum(): # declare shapes for possible data point creation
			self.xAxisBox.insert(tk.END, item)
		self.xAxisBox.pack(side = tk.TOP, pady=10)

		label = tk.Label( frame1, text="Y-Axis (X1)", width=20 )
		label.pack( side=tk.TOP, pady=10 )

		self.yAxisBox = tk.Listbox(frame1, selectmode=tk.SINGLE, exportselection=0)
		for item in self.d.getHeaderNum(): # declare shapes for possible data point creation
			self.yAxisBox.insert(tk.END, item)
		self.yAxisBox.pack(side = tk.TOP, pady=10)

		label = tk.Label( self.frame2, text="Z-Axis (Y)", width=20 )
		label.pack( side=tk.TOP, pady=10 )

		self.zAxisBox = tk.Listbox(self.frame2, selectmode=tk.SINGLE, exportselection=0)
		for item in self.d.getHeaderNum(): # declare shapes for possible data point creation
			self.zAxisBox.insert(tk.END, item)
		self.zAxisBox.pack(side = tk.TOP, pady=10)

		if self.clusterData == None:
			label = tk.Label( self.frame3, text="Color", width=20 )
			label.pack( side=tk.TOP, pady=10 )

			self.colorBox = tk.Listbox(self.frame3, selectmode=tk.SINGLE, exportselection=0)
			for item in self.d.getHeaderNum(): # declare shapes for possible data point creation
				self.colorBox.insert(tk.END, item)
			self.colorBox.pack(side = tk.TOP, pady=10)


		label = tk.Label( self.frame4, text="Size", width=20 )
		label.pack( side=tk.TOP, pady=10 )

		self.sizeBox = tk.Listbox(self.frame4, selectmode=tk.SINGLE, exportselection=0)
		for item in self.d.getHeaderNum(): # declare shapes for possible data point creation
			self.sizeBox.insert(tk.END, item)
		self.sizeBox.pack(side = tk.TOP, pady=10)

		label = tk.Label( frame0, text="Border Color", width=20 )
		label.pack( side=tk.TOP, pady=10 )

		self.borderBox = tk.Listbox(frame0, selectmode=tk.SINGLE, exportselection=0)
		for item in self.d.getHeaderNum(): # declare shapes for possible data point creation
			self.borderBox.insert(tk.END, item)
		self.borderBox.pack(side = tk.TOP, pady=10)

		label = tk.Label( frame1, text="Border Width", width=20 )
		label.pack( side=tk.TOP, pady=10 )

		self.borderWidthBox = tk.Listbox(frame1, selectmode=tk.SINGLE, exportselection=0)
		for item in self.d.getHeaderNum(): # declare shapes for possible data point creation
			self.borderWidthBox.insert(tk.END, item)
		self.borderWidthBox.pack(side = tk.TOP, pady=10)

		if self.clusterData != None:
			self.var = tk.IntVar()
			self.var.set(True)
			smooth = tk.Checkbutton(self.frame4, text="Smooth colors (y/n)", variable=self.var, onvalue=True, offvalue=False)
			smooth.pack(side = tk.TOP, pady=10)

		pass

	def buttonbox(self):
		# add standard button box. override if you don't want the
		# standard buttons

		box = self.frame4

		w = tk.Button(box, text="Sure", width=10, command=self.ok, default=tk.ACTIVE)
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=tk.LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

		pass

	def apply(self):

		try:
			xAxis = self.xAxisBox.get(self.xAxisBox.curselection()[0])
			yAxis = self.yAxisBox.get(self.yAxisBox.curselection()[0])
			try:
				zAxis = self.zAxisBox.get(self.zAxisBox.curselection()[0])
			except IndexError:
				zAxis = None
			try:
				color = self.colorBox.get(self.colorBox.curselection()[0])
			except IndexError:
				color = None
			except:
				color = None
			try:
				size = self.sizeBox.get(self.sizeBox.curselection()[0])
			except IndexError:
				size = None
			try:
				borderColor = self.borderBox.get(self.borderBox.curselection()[0])
			except IndexError:
				borderColor = None
			try:
				borderSize = self.borderWidthBox.get(self.borderWidthBox.curselection()[0])
			except IndexError:
				borderSize = None

			if self.clusterData != None:
				try:
					smooth = self.var.get()
				except IndexError:
					smooth = None
			else:
				smooth = None

			#print smooth


			#color = self.colorOption.get()
			#size = self.sizeOption.get()
			shape = "circle"

			#print xAxis, yAxis, zAxis, color, size, shape, borderColor, borderSize, smooth

			self.result = (xAxis, yAxis, zAxis, color, size, shape, borderColor, borderSize, smooth, self.clusterData)
		except IndexError:
			tkMessageBox.showwarning("Selection Error!","Please pick a value for every listed field.")

 ######  ##     ##  #######   #######   ######  ########    ########  ########  ######
##    ## ##     ## ##     ## ##     ## ##    ## ##          ##     ## ##       ##    ##
##       ##     ## ##     ## ##     ## ##       ##          ##     ## ##       ##
##       ######### ##     ## ##     ##  ######  ######      ########  ######   ##   ####
##       ##     ## ##     ## ##     ##       ## ##          ##   ##   ##       ##    ##
##    ## ##     ## ##     ## ##     ## ##    ## ##          ##    ##  ##       ##    ##
 ######  ##     ##  #######   #######   ######  ########    ##     ## ########  ######

class ChooseRegression(Dialog):
	def __init__(self, parent, d):
		self.d = d
		Dialog.__init__(self, parent, "Choose Axes")

	def body(self, parent):
		#print self.d.getHeaderNum() # test to see if everything eas passed correctly

		# use a label to set the size of the right panel
		#box = tk.Frame(self)
		self.frame0 = tk.Frame(self)
		self.frame0.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y) # draw the side frame

		self.frame1 = tk.Frame(self)
		self.frame1.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y) # draw the side frame

		self.frame2 = tk.Frame(self)
		self.frame2.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y) # draw the side frame

		label = tk.Label( self.frame0, text="X0", width=20 )
		label.pack( side=tk.TOP, pady=10 )

		self.indBox = tk.Listbox(self.frame0, selectmode=tk.SINGLE, exportselection=0)
		for item in self.d.getHeaderNum(): # declare shapes for possible data point creation
			self.indBox.insert(tk.END, item)
		self.indBox.pack(side = tk.TOP, pady=10)

		label = tk.Label( self.frame1, text="y", width=20 )
		label.pack( side=tk.TOP, pady=10 )

		self.indBox1 = tk.Listbox(self.frame1, selectmode=tk.SINGLE, exportselection=0)
		for item in self.d.getHeaderNum(): # declare shapes for possible data point creation
			self.indBox1.insert(tk.END, item)
		self.indBox1.pack(side = tk.TOP, pady=10)

		label = tk.Label( self.frame2, text="X1", width=20 )
		label.pack( side=tk.TOP, pady=10 )

		self.deBox = tk.Listbox(self.frame2, selectmode=tk.SINGLE, exportselection=0)
		for item in self.d.getHeaderNum(): # declare shapes for possible data point creation
			self.deBox.insert(tk.END, item)
		self.deBox.pack(side = tk.TOP, pady=10)

		pass

	def buttonbox(self):
		# add standard button box. override if you don't want the
		# standard buttons

		box = self.frame2

		w = tk.Button(box, text="Sure", width=10, command=self.ok, default=tk.ACTIVE)
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=tk.LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

		pass

	def apply(self):

		try:
			independent = self.indBox.get(self.indBox.curselection()[0])
			dependent = self.deBox.get(self.deBox.curselection()[0])

			try:
				independent1 = self.indBox1.get(self.indBox1.curselection()[0])
			except IndexError:
				independent1 = None

			self.result = (independent, independent1, dependent)
		except IndexError:
			tkMessageBox.showwarning("Selection Error!","Please pick an X0 and y.")

class ChoosePCA(Dialog):
	def __init__(self, parent, d):
		self.d = d
		Dialog.__init__(self, parent, "PCA Analysis")

	def body(self, parent):
		#print self.d.getHeaderNum() # test to see if everything eas passed correctly

		# use a label to set the size of the right panel
		#box = tk.Frame(self)
		self.frame0 = tk.Frame(self)
		self.frame0.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y) # draw the side frame

		self.frame1 = tk.Frame(self)
		self.frame1.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y) # draw the side frame

		self.frame2 = tk.Frame(self)
		self.frame2.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y) # draw the side frame

		label = tk.Label( self.frame0, text="PCA", width=20 )
		label.pack( side=tk.TOP, pady=10 )

		self.pcaBox = tk.Listbox(self.frame0, selectmode=tk.MULTIPLE, exportselection=0)
		for item in self.d.getHeaderNum(): # declare shapes for possible data point creation
			self.pcaBox.insert(tk.END, item)
		self.pcaBox.pack(side = tk.TOP, pady=10)

		def select():
			self.pcaBox.select_set(0, tk.END)

		tk.Button(self.frame0, text='select all', command = select).pack()

		label = tk.Label( self.frame2, text="Name", width=20 )
		label.pack( side=tk.TOP, pady=10 )

		self.e = tk.Entry(self.frame2)
		self.e.insert(tk.END, time.strftime("%X"))

		self.e.pack()

		self.var = tk.IntVar()
		self.var.set(True)
		normalize = tk.Checkbutton(self.frame2, text="Normalize (y/n)", variable=self.var, onvalue=True, offvalue=False)
		normalize.pack()

		pass

	def buttonbox(self):
		# add standard button box. override if you don't want the
		# standard buttons

		box = self.frame2

		w = tk.Button(box, text="Sure", width=10, command=self.ok, default=tk.ACTIVE)
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=tk.LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

		pass

	def apply(self):

		try:
			pcaHeaders = []
			for i in range(len(self.pcaBox.curselection())):
				pcaHeaders.append(self.pcaBox.get(self.pcaBox.curselection()[i]))

			name = (self.e.get()+'.pca')

			normalize = self.var.get()

			self.result = pcaHeaders, name, normalize
		except IndexError:
			tkMessageBox.showwarning("Selection Error!","Please pick at least two headers.")


class DisplayPCA(Dialog):
	def __init__(self, parent, fHeaders, headers, values, vectors):
		self.fHeaders = fHeaders
		self.headers = headers
		self.values = values
		self.vectors = vectors
		Dialog.__init__(self, parent, "PCA Data")

	def body(self, master):
		frameColor = "#1f1f1f"

		self.configure(background=frameColor)
		master.configure(background=frameColor)


		# print self.vectors
		# print self.values
		# print self.headers
		# print self.fHeaders

		for i in range(len(self.fHeaders)+1):
			for j in range(len(self.headers)):
				if i % 2 == 0:
					fontColor = "#2c87c4"
				else:
					fontColor = "#226896"
				if i == 0:
					tk.Label(master, text=self.headers[j], justify=tk.LEFT, font = "Helvetica 14 bold", fg = fontColor, bg = frameColor).grid(row=i, column=j)
				elif j == 0:
					tk.Label(master, text=self.fHeaders[i-1], justify=tk.LEFT, font = "Helvetica 14 bold", fg = fontColor, bg = frameColor).grid(row=i+1, column=j)
				elif j == 1:
					tk.Label(master, text=self.values[i-1], justify=tk.LEFT, font = "Helvetica 14 bold", fg = fontColor, bg = frameColor).grid(row=i+1, column=j)
				else:
					tk.Label(master, text=str(self.vectors[i-2,j-2]), justify=tk.LEFT, fg = fontColor, bg = frameColor).grid(row=i+1, column=j)

	def buttonbox(self):
		# add standard button box. override if you don't want the
		# standard buttons

		frameColor = "#1f1f1f"


		box = tk.Frame(self)

		box.configure(background=frameColor)


		w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
		w.configure(highlightbackground=frameColor)
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
		w.configure(highlightbackground=frameColor)
		w.pack(side=tk.LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

		pass

class ChooseCluster(Dialog):
	def __init__(self, parent, d):
		self.d = d
		self.typeList = ["euclidean", "correlation","cosine","hamming","canberra","manhattan"]
		self.thresholdList = [1e-5, 1e-6, 1e-7, 1e-8, 1e-9]
		self.iterationsList = [50, 100, 150, 200, 300]

		Dialog.__init__(self, parent, "Cluster")


	def body(self, parent):
		#print self.d.getHeaderNum() # test to see if everything eas passed correctly

		# use a label to set the size of the right panel
		#box = tk.Frame(self)
		self.frame0 = tk.Frame(self)
		self.frame0.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y) # draw the side frame

		self.frame1 = tk.Frame(self)
		self.frame1.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y) # draw the side frame

		self.frame2 = tk.Frame(self)
		self.frame2.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y) # draw the side frame

		label = tk.Label( self.frame0, text="PCA", width=20 )
		label.pack( side=tk.TOP, pady=10 )

		self.clusterBox = tk.Listbox(self.frame0, selectmode=tk.MULTIPLE, exportselection=0)
		for item in self.d.getHeaderNum(): # declare shapes for possible data point creation
			self.clusterBox.insert(tk.END, item)
		self.clusterBox.select_set(0)
		self.clusterBox.pack(side = tk.TOP, pady=10)

		def select():
			self.clusterBox.select_set(0, tk.END)

		tk.Button(self.frame0, text='select all', command = select).pack()

		label = tk.Label( self.frame0, text="K-Value", width=20 )
		label.pack( side=tk.TOP, pady=10 )

		self.e = tk.Entry(self.frame0)
		self.e.insert(tk.END, 1)
		self.e.pack()

		label = tk.Label( self.frame2, text="Type/Threshold/Iterations", width=20 )
		label.pack( side=tk.TOP, pady=10 )

		self.typeBox = tk.Listbox(self.frame2, selectmode=tk.SINGLE, exportselection=0, height=4)
		for item in self.typeList: # declare shapes for possible data point creation
			self.typeBox.insert(tk.END, item)
		self.typeBox.select_set(0)
		self.typeBox.pack(side = tk.TOP, pady=10)

		self.threshold = tk.Listbox(self.frame2, selectmode=tk.SINGLE, exportselection=0, height=4)
		for item in self.thresholdList: # declare shapes for possible data point creation
			self.threshold.insert(tk.END, item)
		self.threshold.select_set(2)
		self.threshold.pack(side = tk.TOP, pady=10)

		self.iterations = tk.Listbox(self.frame2, selectmode=tk.SINGLE, exportselection=0, height=4)
		for item in self.iterationsList: # declare shapes for possible data point creation
			self.iterations.insert(tk.END, item)
		self.iterations.select_set(1)
		self.iterations.pack(side = tk.TOP, pady=10)

		pass

	def buttonbox(self):
		# add standard button box. override if you don't want the
		# standard buttons

		box = self.frame2

		w = tk.Button(box, text="Sure", width=10, command=self.ok, default=tk.ACTIVE)
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=tk.LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

		pass

	def apply(self):

		try:
			clusterHeaders = []
			for i in range(len(self.clusterBox.curselection())):
				clusterHeaders.append(self.clusterBox.get(self.clusterBox.curselection()[i]))

			if len(clusterHeaders) < 2:
				print "need more cluster headers"
				return
			K = self.e.get() # make sure it's an int
			print K

			types = self.typeBox.get(self.typeBox.curselection()[0])

			print types
			print clusterHeaders

			threshold = self.threshold.get(self.threshold.curselection()[0])
			iterations = self.iterations.get(self.iterations.curselection()[0])

			print threshold, iterations


			self.result = clusterHeaders, types, K, threshold, iterations
		except IndexError:
			tkMessageBox.showwarning("Selection Error!","Please pick at least two headers.")


class ChooseLearning(Dialog):
	def __init__(self, parent):
		Dialog.__init__(self, parent, "Machine Learning")

	def body(self, parent):
		#print self.d.getHeaderNum() # test to see if everything eas passed correctly

		# use a label to set the size of the right panel
		#box = tk.Frame(self)
		self.frame0 = tk.Frame(self)
		self.frame0.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y) # draw the side frame

		self.frame1 = tk.Frame(self)
		self.frame1.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y) # draw the side frame

		self.frame2 = tk.Frame(self)
		self.frame2.pack(side=tk.LEFT, padx=2, pady=2, fill=tk.Y) # draw the side frame

		self.type = tk.IntVar()

		tk.Radiobutton(self.frame2, text="KNN", variable=self.type, value=1).pack()
		tk.Radiobutton(self.frame2, text="NaiveBayes", variable=self.type, value=2).pack()

		self.type.set(1)

        #self.inFilePath = tk.StringVar()

		e1 = tk.Entry(self.frame0)
		e1.pack()

		e2 = tk.Entry(self.frame0)
		e2.pack()

		e3 = tk.Entry(self.frame0)
		e3.pack()

		e4 = tk.Entry(self.frame0)
		e4.pack()

		# e.delete(0, END)
		# e.insert(0, "a default value")

		def trainData():
			fn = tkFileDialog.askopenfilename( parent=self.frame1, title='Train Data', initialdir='.' )
			self.trainDataFile = fn
			e1.delete(0, tk.END)
			e1.insert(0, fn.split('/')[-1])

		def trainCat():
			fn = tkFileDialog.askopenfilename( parent=self.frame1, title='Train Categories', initialdir='.' )
			self.trainCatFile = fn
			e3.delete(0, tk.END)
			e3.insert(0, fn.split('/')[-1])


		def testData():
			fn = tkFileDialog.askopenfilename( parent=self.frame1, title='Test Data', initialdir='.' )
			self.testDataFile = fn
			e2.delete(0, tk.END)
			e2.insert(0, fn.split('/')[-1])


		def testCat():
			fn = tkFileDialog.askopenfilename( parent=self.frame1, title='Test Categories', initialdir='.' )
			self.testCatFile = fn
			e4.delete(0, tk.END)
			e4.insert(0, fn.split('/')[-1])


		tk.Button(self.frame1, text='Train Data', command = trainData).pack(side = tk.TOP, pady=4)
		tk.Button(self.frame1, text='Test Data', command = testData).pack(side = tk.TOP, pady=4)
		tk.Button(self.frame1, text='Train Categories', command = trainCat).pack(side = tk.TOP, pady=4)
		tk.Button(self.frame1, text='Test Categories', command = testCat).pack(side = tk.TOP, pady=4)





	def buttonbox(self):
		# add standard button box. override if you don't want the
		# standard buttons

		box = self.frame2

		w = tk.Button(box, text="Sure", width=10, command=self.ok, default=tk.ACTIVE)
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=tk.LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

		pass

	def apply(self):

		try:
			if self.type.get() == 1:
				self.type = "KNN"
			else:
				self.type = "NaiveBayes"
			try:
				self.result = self.trainDataFile, self.testDataFile, self.trainCatFile, self.testCatFile, self.type
			except:
				self.result = self.trainDataFile, self.testDataFile, self.type
		except IndexError:
			tkMessageBox.showwarning("Selection Error!","Please pick at least two data files.")


if __name__ == "__main__":
	dapp = DisplayApp(1200, 675)
	dapp.main()
