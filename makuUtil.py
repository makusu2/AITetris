import conf
from conf import *
#import pyscreenshot as ImageGrab
#import ImageGrab
import thread
import time
#import screenshot
class Directions:
	D = "Down"
	L = "Left"
	R = "Right"
	U = "Up"
	directions = [D,L,R]
	allDirections = [D,L,R,U]
	rowMod = {D:1,L:0,R:0,U:-1}
	colMod = {D:0,L:-1,R:1,U:0}
	toDirection = {"Down":D,"Left":L,"Right":R,'a':L,'A':L,'d':R,'D':R,'s':D,'S':D}
	S = "Rotate"
	legalMoves = [D,L,R,S]
	rotations = [S]
	toRotation = {'r':S,'R':S,"rotate":S,"Rotate":S}
	direDict = {}
	for k in toDirection:
		direDict[k] = toDirection[k]
	for k in toRotation: 
		direDict[k] = toRotation[k]
class QuadCoords:
	def __init__(self,coords): #For now, it's just going to be to make it work. Optimize later.
		coords = tuple([tuple(coord) for coord in coords])
		emptyCoords = (coords == []) or (coords == tuple([]))
		#newCoords = []
		#self.topRow = None
		#self.botRow = None
		#self.leftCol = None
		#self.rightCol = None
		#if not emptyCoords:
		#	cols = [coords[i][0] for i in range(len(coords))]
		#	rows = [coords[i][1] for i in range(len(coords))]
		#	self.leftCol = min(cols)
		#	self.rightCol = max(cols)
		#	self.topRow = min(rows)
		#	self.botRow = max(rows)
			#newCoords = [(col,row) for col in range(self.leftCol,self.rightCol+1) for row in range(self.topRow,self.botRow+1)]
		#	for col in range(self.leftCol,self.rightCol+1):
		#		for row in range(self.topRow,self.botRow+1):
		#			if (col,row) in coords:
		#				newCoords = newCoords + [(col,row)]
		#self.coords = tuple(newCoords)
		self.coords = coords
	
	def __contains__(self,key): return (tuple(key) in self.coords)
	def __getitem__(self,index): return self.coords[index]
	def __len__(self): return len(self.coords)
	def __len_hint__(self): return 4
	def __iter__(self): return self.coords.__iter__()
	def __str__(self): return "QuadCoords: "+str(self.coords)
	def __hash__(self): return self.coords.__hash__()
	def __eq__(self,other): 
		for coord in self:
			if not coord in other:
				return False
		return True
		for i in range(len(self.coords)):
			if not (self.coords[i] == other.coords[i]):
				return False
		return True
		#return (self.coords == other)
	def botRow(self): return max([self[i][1] for i in range(len(self))])
	def topRow(self): return min([self[i][1] for i in range(len(self))])
	def leftCol(self): return min([self[i][0] for i in range(len(self))])
	def rightCol(self): return max([self[i][0] for i in range(len(self))])
	def pushedDownCoords(self,downPush): return QuadCoords([[coord[0],coord[1]+downPush] for coord in self.coords])
	def pushedToDirectionCoords(self,direction):
		newCoords = [[coord[0]+Directions.colMod[direction],coord[1]+Directions.rowMod[direction]] for coord in self.coords]
		return QuadCoords(newCoords)
	def evaluationFunction(self): return sum([coord[1] for coord in self.coords])
	def rotatedCoords(self,boolDict):
		def moveCoordsForLegality(newBoxes):
			impossibilityCounter = 0
			def getMovedCoords(movedToDirection):
				newMovedToDirection = {Directions.allDirections[i]:movedToDirection[Directions.allDirections[i]].pushedToDirectionCoords(d) for i in range(len(Directions.allDirections))}
				return newMovedToDirection
			conflicts = False
			#print "newBoxes: ",newBoxes
			movedToDirection = {d:newBoxes.pushedToDirectionCoords(d) for d in Directions.allDirections}
			#print "movedToDirection: ",movedToDirection
			while True:
				for d in movedToDirection:
					conflicts = False
					for newTetro in movedToDirection[d]:
						if coordsAreIllegal(boolDict,newTetro):
							conflicts = True
					if not conflicts:
						return movedToDirection[d]
				movedToDirection = getMovedCoords(movedToDirection)
				impossibilityCounter+=1
				if impossibilityCounter>5:
					return False
		origin = self[0]
		newCoords = []
		for box in self:
			horDiff = box[0]-origin[0]
			vertDiff = origin[1]-box[1]
			newCoord = [origin[0]+vertDiff,origin[1]+horDiff]
			newCoords.append(newCoord)
		#print "1"
		newCoords = QuadCoords(newCoords)
		#print "newCoords: ",newCoords
		legalCoords = moveCoordsForLegality(newCoords)
		#print "1"
		if not legalCoords: return False
		return QuadCoords(legalCoords)
	def hasIllegalCoords(self,boolDict,checkStateTetro=False,extraCoords=[]):
		for coord in self:
			if coordsAreIllegal(boolDict,coord,checkStateTetro=checkStateTetro,extraCoords=extraCoords):
				return True
		return False
def coordsAreIllegal(boolDict, coords, checkStateTetro=False, extraCoords=[]):
	#print "coords: ",coords
	outOfGrid = (coords[0]<0 or coords[0]>=boardWidth or coords[1]<0 or coords[1]>=boardDepth or bool(boolDict[coords]))
	return (outOfGrid or (checkStateTetro and (coords in boolDict.tetroBoxList)) or (coords in extraCoords))
def getCoordToDirection(coord, direction):
	if direction in Directions.rotations:
		print "You tried to get a coord to a direction for a rotation. Don't do that."
	newCoord = tuple([coord[0]+Directions.colMod[direction],coord[1]+Directions.rowMod[direction]])
	return newCoord
def avg(list):
	return float(sum(list))/len(list)