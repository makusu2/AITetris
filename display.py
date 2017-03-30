import Tkinter
from Tkinter import *
from board import *
import agent
from agent import *
import thread
import makuUtil
from makuUtil import *
import conf
from conf import *
import math
import time
#Note: A "Box" is just a space. A "block" is a box that holds a piece. A "Tetro" is one of the four-blocked pieces in a Tetris game.
#I need to work on the dimensions. I think I"m confusing rows and columns. It can either be [column,row] or [row][column]
#Rows should count down.
class Display:
	def __init__(self, master=Tk(),board=Board()):
		self.master = master
		self.board = board
		self.gameGrid = GameGrid(self)
		self.fallingBlocks = QuadCoords([])#[] #This will hold the four blocks of the current tetro
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
	def __getitem__(self,index):
		return self.gameGrid[index]
	def rowCleared(self):
		print "You've cleared a row!"
		self.points+=1
		self.scoreText.set("Score: "+str(self.points))
	def pressedKey(self,key):
		self.pressedKeyChar(key.char)
	def pressedKeyChar(self,keyChar):
		if keyChar in Directions.direDict:
			self.directionPressed(Directions.direDict[keyChar])
	def beginGame(self):self.endTurn(firstTurn=True)
	def directionPressed(self,d):
		if d not in Directions.directions:
			if d in Directions.rotations:
				self.rotate()
				return
			else:
				print "You pressed a direction, but it's invalid."
				return
		oldBoxes = self.fallingBlocks
		for oldBox in oldBoxes:
			newBox = makuUtil.getCoordToDirection(oldBox,d)
			if makuUtil.coordsAreIllegal(self,newBox):
				if d==Directions.D:
					self.endTurn()
					return
				else:
					print "ILLEGAL MOVE 323222"
					return
		newBoxes = [makuUtil.getCoordToDirection(oldBox,d) for oldBox in oldBoxes]
		self.changeActivatedCoords(oldBoxes,newBoxes)
		self.fallingBlocks = QuadCoords(newBoxes)
	def rotate(self):
		newCoords = self.fallingBlocks.rotatedCoords(self)
		#newBoxes = [self.gameGrid[newCoord] for newCoord in newCoords]
		newBoxes = newCoords
		oldBoxes = self.fallingBlocks
		self.fallingBlocks = QuadCoords(newBoxes)
		self.changeActivatedCoords(oldBoxes,newBoxes)
	def changeActivatedCoords(self,oldBoxes,newBoxes):
		for oldBox in oldBoxes: self[oldBox].activate()
		for newBox in newBoxes: self[newBox].activate()
	def endTurn(self,firstTurn=False): #This is called when a piece lands at the bottom
		#This is not yet optimized. It is only for testing.
		def commitTetro(display):
			display.fallingBlocks = QuadCoords([])
		if not firstTurn:
			commitTetro(self)
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
	def addTetro(self, tetro):
		blockList = []
		for startingPos in tetro.spaces:
			currentBox = self.gameGrid[startingPos]
			if bool(currentBox):
				self.endGame()
			currentBox.activate()
			blockList.append(currentBox)
		self.fallingBlocks = QuadCoords(blockList)
	def endGame(self):
		print "YOU LOSE!"
		time.sleep(100)
			
class GameGrid:
	def __init__(self,father,master=Tk()):
		self.master = master
		self.father = father
		self.boxes = {(col,row):Box(self.master,self.father,(col,row)) for col in range(boardWidth) for row in range(boardDepth)}
		for row in range(boardDepth):
			for col in range(boardWidth):
				self.boxes[col,row].grid()
	def __getitem__(self,index): #This might cause problems with the tetro on top
		return self.boxes[index]
	def __setitem__(self,index,value):
		if value:
			self.boxes[tuple(index)].makeTrue()
		else:
			self.boxes[tuple(index)].makeFalse()
	def __str__(self):
		s=""
		for row in range(boardDepth):
			for col in range(boardWidth):
				s+=str(self[col,row])
			s+="\n"
		return s
	def rowIsFull(self,row):
		thing3 = []
		for col in range(boardWidth):
			thing1 = self[col,row]
			thing2 = bool(thing1)
			thing3 = thing3 + [thing2]
		return not (False in [bool(self[col,row]) for col in range(boardWidth)])
	def emptyRow(self, row):
		for col in range(boardWidth):
			if bool(self.boxes[col,row]):
				self.boxes[col,row].activate()
class Box:
	def __init__(self,master,display,coords):
		self.intVar = IntVar()
		self.isChecked = False #This is stupid, but I've tried for HOURS getting the other way to work and it won't. LIterally hours. 2/25/17 from 8am to 3:13pm.
		self.master = master
		self.checkBox = Checkbutton(self.master,variable=self.intVar,command=self.hitBox)
		self.checkBox.var = self.intVar
		self.display = display
		self.coords = coords
	def grid(self):
		self.checkBox.grid(row=self[1],column=self[0])
	def hitBox(self):
		self.isChecked = not self.isChecked
	def __str__(self):
		return "#" if bool(self) else "0"
	def activate(self): self.checkBox.invoke()
	def __getitem__(self,b):
		return self.coords[b]
	def __nonzero__(self):
		if (self[0],self[1]) in self.display.fallingBlocks:
			return False
		return self.isChecked
	def makeTrue():
		if not bool(self):
			self.activate()
	def makeFalse():
		if bool(self):
			self.activate()