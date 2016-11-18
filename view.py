import numpy as np
import math
from copy import deepcopy


debug = False
class View:
	def __init__(self, height = 400, width = 400):
		self.height = height
		self.width = width

		self.reset()
		self.build()
		#self.rotateVRC(-3.14159265359, -3.14159265359)
		#self.build()

		#self.rotateVRC(90, 80)



	#---------reset default values---------#
	def reset(self):
		self.vrp = np.matrix([0.5, 0.5, 1])
		self.vpn = np.matrix([0, 0, -1])
		self.vup = np.matrix([0, 1, 0])
		self.u = np.matrix([1, 0, 0])
		self.extent = np.matrix([1, 1, 1])
		#self.screen = [self.height, self.width]  <-- this is how it was.  Looks backwards - usually X comes before Y
		self.screen = [self.width, self.height]
		self.offset = [20, 20]

	#---------return a view matrix---------#
	def build(self):
		#---------4x4 identity matrix and move matrix to origin and premultiply---------#
		vtm = np.identity( 4, float )
		t1 = self.tMatrix(-self.vrp[0,0], -self.vrp[0,1], -self.vrp[0,2])

		vtm = t1 * vtm

		#---------calculate new reference axes---------#
		if debug:
			print "vup, vpn", self.vup, self.vpn
		tu = np.cross(self.vup, self.vpn)
		tvup = np.cross(self.vpn, tu)
		tvpn = self.vpn

		#---------overwrite default values with orthonormal values---------#
		self.u = self.normalize(tu)
		self.vup = self.normalize(tvup)
		self.vpn = self.normalize(tvpn)


		#---------generate roation (alignment) matrix---------#
		r1 = self.aMatrix(tu, tvup, tvpn)

		#---------multiply various matrices to end with view matrix---------#

		vtm = r1 * vtm

		#vtm = self.tMatrix(0.5*self.extent[0],self.extent[1], 0)*vtm  <-- this is how it was
		vtm = self.tMatrix(0.5*self.extent[0,0],0.5*self.extent[0,1], 0)*vtm
		vtm = self.sMatrix( -self.screen[0] / self.extent[0,0], -self.screen[1] / self.extent[0,1], 1.0 / self.extent[0,2] ) * vtm
		vtm = self.tMatrix( self.screen[0] + self.offset[0], self.screen[1] + self.offset[1], 0 ) * vtm
		if debug:
			print "from view.py"
			print "Screen width = ",self.width," height = ",self.height,"\n"
			print "vtm:"
			print vtm

			print "vtm (transposed):"
			print vtm.T


		return vtm


	def rotateVRC(self, vupAngle, uAngle):
		self.vrp0 = self.vrp
		self.up0 = self.vup
		self.u0 = self.u
		self.vpn0 = self.vpn


		val = self.vrp + self.vpn * self.extent[0,2] * 0.5
		t1 = self.tMatrix(-val[0,0], -val[0,1], -val[0,2]) #self.vrp + self.vpn * self.extent[0,2] * 0.5
		Rxyz = self.aMatrix(self.u, self.vup, self.vpn) # make axis alignment matrix
		r1 = self.Ry(vupAngle)
		r2 = self.Rx(uAngle)
		t2 = np.linalg.inv(t1)
		tvrc = np.matrix([[self.vrp[0,0], self.vrp[0,1], self.vrp[0,2], 1],
					[self.u[0,0], self.u[0,1], self.u[0,2], 0.0],
					[self.vup[0,0], self.vup[0,1], self.vup[0,2], 0.0],
					[self.vpn[0,0], self.vpn[0,1], self.vpn[0,2], 0.0]])

		tvrc = (t2*Rxyz.T*r2*r1*Rxyz*t1*tvrc.T).T

		self.vrp = tvrc[0,:3]
		self.u = self.normalize(tvrc[1,:3])
		self.vup = self.normalize(tvrc[2,:3])
		self.vpn = self.normalize(tvrc[3,:3])
		#print "tvrc: \n", tvrc
		#print "\n normalized values: \n %s \n %s \n %s" % (self.u, self.vup, self.vpn)
		self.build()



	#---------transformation matrix outline---------#
	def tMatrix(self, a, b, c):
		matrix = np.matrix( [[ 1, 0, 0, a], [ 0, 1, 0, b], [ 0, 0, 1, c ], [ 0, 0, 0, 1 ]] )
		return matrix

	#---------scaling matrix outline---------#
	def sMatrix(self, a, b, c):
		matrix = np.matrix( [[ a, 0, 0, 0], [ 0, b, 0, 0], [ 0, 0, c, 0 ], [ 0, 0, 0, 1 ]] )
		return matrix

	#---------alignment matrix outline---------#
	def aMatrix(self, u, vup, vpn):
		matrix = np.matrix( [[ u[0, 0], u[0, 1], u[0, 2], 0.0 ], [ vup[0, 0], vup[0, 1], vup[0, 2], 0.0 ], [ vpn[0, 0], vpn[0, 1], vpn[0, 2], 0.0 ], [ 0.0, 0.0, 0.0, 1.0 ]])
		return matrix

	#---------rotate about the Y-axis---------#
	def Ry(self, theta):
		matrix = np.matrix( [[ math.cos(theta), 0.0, math.sin(theta), 0.0 ], [ 0.0, 1, 0.0, 0.0 ], [ -math.sin(theta), 0.0, math.cos(theta), 0.0 ], [ 0.0, 0.0, 0.0, 1.0 ]])
		return matrix

	#---------rotate about the X-axis---------#
	def Rx(self, theta):
		matrix = np.matrix( [[ 1, 0.0, 0.0, 0.0 ], [ 0.0, math.cos(theta), -math.sin(theta), 0.0], [ 0.0, math.sin(theta), math.cos(theta), 0.0 ], [ 0.0, 0.0, 0.0, 1.0 ]])
		return matrix

	#---------normalization function---------#
	def normalize(self, val):
		norm = np.linalg.norm(val)
		return val/norm

	#---------clone method---------#
	def clone(self):
		viewClone = deepcopy(View())
		return viewClone

if __name__ == "__main__":
	view = View()
