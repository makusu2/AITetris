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
		self.fallingTetro = None
		self.fallingBlocks = [] #This will hold the four blocks of the current tetro
		self.input = Agent(self)#KeyboardInput(self)
		self.master.title("Tetris")
		self.master.geometry("300x300")
		Label(master, text = "Play Tetris!\n\n").pack()
		
		self.points = 0
		
		self.scoreText = StringVar()
		self.scoreText.set("Score: "+str(self.points))
		self.scoreLabel = Label(self.master,textvariable=self.scoreText)
		self.scoreLabel.pack()
		
		self.master.after(1,self.beginGame)
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
		downMost = max([oldBox.row for oldBox in oldBoxes])
		leftMost = min([oldBox.col for oldBox in oldBoxes])
		rightMost = max([oldBox.col for oldBox in oldBoxes])
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
		boolGrid = self.gameGrid.asDict()
		newCoords = makuUtil.getRotatedCoords(boolGrid,self.fallingBlocks)
		newBoxes = [self.gameGrid.boxes[tuple(newCoord)] for newCoord in newCoords]
		oldBoxes = self.fallingBlocks
		self.fallingBlocks = newBoxes
		for oldBox in oldBoxes: oldBox.activate()
		for newBox in newBoxes: newBox.activate()
		
	def directionBlocked(self,oldBoxes,newBoxes):
		for newBox in newBoxes:
			if newBox not in oldBoxes:
				if bool(newBox):#.get():
					return True
		return False
	def endTurn(self): #This is called when a piece lands at the bottom
		#This is not yet optimized. It is only for testing.
		for row in range(1,boardDepth):
			if self.gameGrid.rowIsFull(row):
				self.rowCleared()
				for row2 in range(row,0,-1):
					for col in range(boardWidth):
						toBeReplaced = self.gameGrid.boxes[col,row2]
						toReplace = self.gameGrid.boxes[col,row2-1]
						if not (bool(toBeReplaced) == bool(toReplace)):
							toBeReplaced.activate()
				self.gameGrid.emptyRow(0) #Clearing the top row
		self.addTetro(Tetro.randomTetro(self.board))
		thread.start_new_thread(self.input.newTurn, ())
		#self.input.newTurn()
	def addTetro(self, tetro):
		self.fallingTetro = tetro
		self.fallingBlocks = []
		for startingPos in tetro.spaces:
			currentBox = self.gameGrid[startingPos]
			if bool(currentBox):
				self.endGame()
			currentBox.activate()
			self.fallingBlocks.append(currentBox)
		self.fallingTetro = tetro
	def getBoxDown(self, oldBox):
		return self.getBoxToDirection(oldBox,Direction.D)
	def getBoxToDirection(self,oldBox,d):
		dimensions = [oldBox.col,oldBox.row]
		return self.gameGrid[dimensions[0]+Directions.colMod[d],dimensions[1]+Directions.rowMod[d]]
	def endGame(self):
		print "YOU LOSE!"
		sleep(10)
			
class GameGrid:
	def __init__(self,father,master=Tk()):
		self.master = master
		self.father = father
		self.boxes = {(col,row):Box(self.master,row,col) for col in range(boardWidth) for row in range(boardDepth)}
		for row in range(boardDepth):
			for col in range(boardWidth):
				self.boxes[col,row].grid()
	def __getitem__(self,index):
		return self.boxes[tuple(index)]
	def asDict(self): #THIS WILL BE WITHOUT TETRO
		boolGridDict = {}
		for row in range(boardDepth):
			for col in range(boardWidth):
				boolGridDict[col,row] = self[col,row]
		for box in self.father.fallingBlocks:
			boolGridDict[(box.col,box.row)] = False
		return boolGridDict
	def __str__(self):
		s=""
		for row in range(boardDepth):
			for col in range(boardWidth):
				s+=str(self[col,row])
			s+="\n"
		return s
	def rowIsFull(self,row):
		return not (False in [bool(self[col,row]) for col in range(boardWidth)])
	def emptyRow(self, row):
		for col in range(boardWidth):
			if bool(self.boxes[col,row]):#.get():
				self.boxes[col,row].activate()
class Box:
	def __init__(self,master,row,col):
		self.intVar = IntVar()
		self.isChecked = False #This is stupid, but I've tried for HOURS getting the other way to work and it won't. LIterally hours. 2/25/17 from 8am to 3:13pm.
		self.master = master
		self.checkBox = Checkbutton(self.master,variable=self.intVar,command=self.hitBox)
		self.checkBox.var = self.intVar
		self.col = col
		self.row = row
	def grid(self):
		self.checkBox.grid(row=self.row,column=self.col)
	def hitBox(self):
		self.isChecked = not self.isChecked
	def __str__(self):
		return "#" if bool(self) else "0"
	def activate(self): self.checkBox.invoke()
	def __getitem__(self,b):
		return tuple([self.col,self.row])[b]
	def __nonzero__(self):
		return self.isChecked