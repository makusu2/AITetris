import Tkinter
from Tkinter import *
from board import *
import agent
from agent import *
import thread
import makuUtil
from makuUtil import Directions
import conf
from conf import *
import math
#Note: A "Box" is just a space. A "block" is a box that holds a piece. A "Tetro" is one of the four-blocked pieces in a Tetris game.
#I need to work on the dimensions. I think I"m confusing rows and columns. It can either be [column,row] or [row][column]
#Rows should count down.
class Display:
	def __init__(self, master=Tk(),board=Board()):
		self.master = master
		self.board = board
		self.gameGrid = GameGrid(self)
		#print "1"
		self.input = KeyboardInput(self)#Agent(self)#KeyboardInput(self)
		self.fallingTetro = None
		self.fallingBlocks = [] #This will hold the four blocks of the current tetro
		
		self.master.title("Tetris")
		self.master.geometry("300x300")
		Label(master, text = "Play Tetris!\n\n").pack()
		
		#print "2"
		self.points = 0
		
		self.scoreText = StringVar()
		self.scoreText.set("Score: "+str(self.points))
		self.scoreLabel = Label(self.master,textvariable=self.scoreText)
		self.scoreLabel.pack()
		
		self.master.after(1,self.beginGame)
		#print "3"
		mainloop()
	def rowCleared(self):
		print "You've cleared a row!"
		self.points+=1
		self.scoreText.set("Score: "+str(self.points))
	def pressedKey(self,key):
		self.pressedKeyChar(key.char)
	def pressedKeyChar(self,keyChar):
		if keyChar in Directions.direDict:
			self.directionPressed(Directions.direDict[keyChar])
	def beginGame(self):self.endTurn()
	def directionPressed(self,d):
		if d not in Directions.directions:
			if d in Directions.rotations:
				self.rotate()
				return
			else:
				print "You pressed a direction, but it's invalid."
				return
		oldBoxes = self.fallingBlocks
		downMost = max([oldBox.dim["row"] for oldBox in oldBoxes])
		leftMost = min([oldBox.dim["col"] for oldBox in oldBoxes])
		rightMost = max([oldBox.dim["col"] for oldBox in oldBoxes])
		if (downMost == boardDepth-1) & (d == Directions.D):
			self.endTurn()
			return
		elif (leftMost==0) & (d==Directions.L):
			print "User tried to go left at the furthest left possible"
			return
		elif (rightMost==boardWidth-1) & (d==Directions.R):
			print "User tried to go right at furthest right possible"
			return
		newBoxes = [self.getBoxToDirection(oldBox,d) for oldBox in oldBoxes]
		if self.directionBlocked(oldBoxes,newBoxes):
			if (d==Directions.D):
				self.endTurn()
				return
			else:
				print "That direction is blocked."
				return
		for oldBox in oldBoxes: oldBox.activate()
		for newBox in newBoxes: newBox.activate()
		self.fallingBlocks = newBoxes
	def rotate(self):
		"""def getRotatedCoords(): #DON'T CHANGE THIS WITHOUT CHANGING THE AGENT
			def moveCoordsForLegality(newBoxes):
				def getMovedCoords(movedToDirection):
					newMovedToDirection = {d:[[newTetro[0]+Directions.colMod[d],newTetro[1]+Directions.rowMod[d]] for newTetro in movedToDirection[d]] for d in Directions.allDirections}
					return newMovedToDirection
				boolDict = self.gameGrid.asDict()
				conflicts = False
				movedToDirection = {d:[[newTetro[0],newTetro[1]] for newTetro in newBoxes] for d in Directions.allDirections}
				while True:
					for d in movedToDirection:
						conflicts = False
						for newTetro in movedToDirection[d]:
							if self.coordsAreIllegal(tuple(newTetro)):
								conflicts = True
						if not conflicts:
							return movedToDirection[d]
					movedToDirection = getMovedCoords(movedToDirection)
			boxes = [[box[0],box[1]] for box in self.fallingBlocks]
			
			origin = boxes[0]
			newCoords = []
			for box in boxes:
				horDiff = box[0]-origin[0]
				vertDiff = origin[1]-box[1]
				newCoord = [origin[0]+vertDiff,origin[1]+horDiff]
				newCoords.append(newCoord)
			
			return moveCoordsForLegality(newCoords)"""
		boolGrid = self.gameGrid.asDictWithoutTetro()
		newCoords = makuUtil.getRotatedCoords(boolGrid,self.fallingBlocks)
		newBoxes = [self.gameGrid.boxes[newCoord[1]][newCoord[0]] for newCoord in newCoords]
		oldBoxes = self.fallingBlocks
		self.fallingBlocks = newBoxes
		for oldBox in oldBoxes: oldBox.activate()
		for newBox in newBoxes: newBox.activate()
			#newBox[1]
		#Since tetris games have different rules for rotation,
		#we will have to press rotate, then get a screenshot for the new board.
		#Also, we will only rotate in one direction.
		#TODO get a screenshot of the board after having pressed "rotate"
		
	def directionBlocked(self,oldBoxes,newBoxes):
		for newBox in newBoxes:
			if newBox not in oldBoxes:
				if newBox.get():
					return True
		return False
	def endTurn(self): #This is called when a piece lands at the bottom
		#This is not yet optimized. It is only for testing.
		for row in range(1,boardDepth):
			if self.gameGrid.rowIsFull(row):
				self.rowCleared()
				for row2 in range(row,0,-1):
					for col in range(boardWidth):
						toBeReplaced = self.gameGrid.boxes[row2][col]
						toReplace = self.gameGrid.boxes[row2-1][col]
						if not (toBeReplaced.get() == toReplace.get()):
							toBeReplaced.activate()
				self.gameGrid.emptyRow(0) #Clearing the top row
		self.addTetro(Tetro.randomTetro(self.board))
		thread.start_new_thread(self.input.newTurn, ())
		#self.input.newTurn()
	def addTetro(self, tetro):
		self.fallingTetro = tetro
		self.fallingBlocks = []
		for startingPos in tetro.spaces:
			currentBox = self.getBox(startingPos)
			if currentBox.get():#If there's already something there
				print "A tetro should have been added, but there was a box already checked."
			currentBox.activate()
			self.fallingBlocks.append(currentBox)
		self.fallingTetro = tetro
	def getBox(self, dimensions): 
		return self.gameGrid.getBox(dimensions)
	def getBoxDown(self, oldBox):
		return self.getBoxToDirection(oldBox,Direction.D)
	def getBoxToDirection(self,oldBox,d):
		dimensions = [oldBox.dim["col"],oldBox.dim["row"]]
		return self.gameGrid.getBox([dimensions[0]+Directions.colMod[d],dimensions[1]+Directions.rowMod[d]])
	def coordsAreIllegal(self,coords):
		#print "checking coords: ",coords
		#for coord in coords:
		if coords[0]<0 or coords[0]>=boardWidth or coords[1]<0 or coords[1]>=boardDepth or self.gameGrid.asDict()[tuple(coords)]:
			#print "coords are illegal."
			return True
		#print "coords are legal."
		return False
			
class GameGrid:
	def __init__(self,father,master=Tk()):
		self.master = master
		self.father = father
		self.boxes = [[Box(self.master,row,col) for col in range(boardWidth)] for row in range(boardDepth)]
		for row in range(boardDepth):
			for col in range(boardWidth):
				self.boxes[row][col].grid()
	#def asList(self):
		
	def printGrid(self):
		print(str(self))
	def getBoolGrid(self):
		boolGrid = [[False for col in range(boardWidth)] for row in range(boardDepth)]
		for row in range(boardDepth):
			for col in range(boardWidth):
				boolGrid[row][col] = self.boxes[row][col].get()
		return boolGrid
	def asDictWithoutTetro(self):
		boolGrid = self.asDict()
		for tetro in self.father.fallingBlocks:
			boolGrid[tuple(tetro)] = False
		return boolGrid
	def asDict(self):
		#boolGrid = [[False for col in range(self.father.board.width)] for row in range(self.father.board.depth)]
		boolGridDict = {}
		for row in range(boardDepth):
			for col in range(boardWidth):
				boolGridDict[col,row] = self.boxes[row][col].get()
		return boolGridDict
		
	def __str__(self):
		boolGrid = self.getBoolGrid()
		s=""
		for row in range(boardDepth):
			for col in range(boardWidth):
				s+=str(self.boxes[row][col])
			s+="\n"
		return s
	def rowIsFull(self,row):
		boolGrid = self.getBoolGrid()
		for col in range(boardWidth):
			if not boolGrid[row][col]: return False
		return True
	def getBox(self, dimensions):
		return self.boxes[dimensions[1]][dimensions[0]]
	def emptyRow(self, row):
		for col in range(boardWidth):
			if self.boxes[row][col].get():
				self.boxes[row][col].activate()
class Box:
	def __init__(self,master,row,col):
		self.intVar = IntVar()
		self.isChecked = False #This is stupid, but I've tried for HOURS getting the other way to work and it won't. LIterally hours. 2/25/17 from 8am to 3:13pm.
		self.master = master
		self.checkBox = Checkbutton(self.master,variable=self.intVar,command=self.hitBox)
		self.checkBox.var = self.intVar
		self.dim={"row":row,"col":col}
	def get(self):
		return self.isChecked
	def grid(self):
		self.checkBox.grid(row=self.dim["row"],column=self.dim["col"])
	def hitBox(self):
		self.isChecked = not self.isChecked
	def __str__(self):
		return "#" if self.get() else "0"
	def activate(self): self.checkBox.invoke()
	def __getitem__(self,b):
		return tuple([self.dim["col"],self.dim["row"]])[b]
	