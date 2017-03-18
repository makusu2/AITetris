import Tkinter
from Tkinter import *
from board import *
import agent
from agent import *
#Note: A "Box" is just a space. A "block" is a box that holds a piece. A "Tetro" is one of the four-blocked pieces in a Tetris game.
#I need to work on the dimensions. I think I"m confusing rows and columns. It can either be [column,row] or [row][column]
#Rows should count down.
class Display:
	def __init__(self, master=Tk(),board=Board()):
		self.master = master
		self.board = board
		self.input = KeyboardInput(self) #Make it a choice later
		self.fallingTetro = None
		self.fallingBlocks = [] #This will hold the four blocks of the current tetro
		
		self.master.title("Tetris")
		self.master.geometry("300x300")
		Label(master, text = "Play Tetris!\n\n").pack()
		
		self.gameGrid = GameGrid(self)
		
		self.points = 0
		
		self.scoreText = StringVar()
		self.scoreText.set("Score: "+str(self.points))
		self.scoreLabel = Label(self.master,textvariable=self.scoreText)
		self.scoreLabel.pack()
		
		#Label(self.master,text="Click here for keyboard input").pack()
		#master.bind("<Key>",self.pressedKey)
		
		
		self.beginGame()
		mainloop()
	def rowCleared(self):
		print "You've cleared a row!"
		self.points+=1
		self.scoreText.set("Score: "+str(self.points))
		#self.scoreLabel.config["text"]("Score: "+str(self.points))
	def pressedKey(self,key):
		keyChar = key.char
		if keyChar in Direction.keyCharToDirection:
			self.directionPressed(Direction.keyCharToDirection[keyChar])
	def beginGame(self):self.endTurn()
	def directionPressed(self,d):
		if d not in Direction.directions:
			print "You pressed a direction, but it's invalid."
			return
		oldBoxes = self.fallingBlocks
		downMost = max([oldBox.dim["row"] for oldBox in oldBoxes])
		leftMost = min([oldBox.dim["col"] for oldBox in oldBoxes])
		rightMost = max([oldBox.dim["col"] for oldBox in oldBoxes])
		if (downMost == self.board.depth-1) & (d == Direction.D):
			self.endTurn()
			return
		elif (leftMost==0) & (d==Direction.L):
			print "User tried to go left at the furthest left possible"
			return
		elif (rightMost==self.board.width-1) & (d==Direction.R):
			print "User tried to go right at furthest right possible"
			return
		newBoxes = [self.getBoxToDirection(oldBox,d) for oldBox in oldBoxes]
		if self.directionBlocked(oldBoxes,newBoxes):
			if (d==Direction.D):
				self.endTurn()
				return
			else:
				print "That direction is blocked."
				return
		for oldBox in oldBoxes: oldBox.activate()
		for newBox in newBoxes: newBox.activate()
		self.fallingBlocks = newBoxes
	def rotate(self):
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
		for row in range(1,self.board.depth):
			if self.gameGrid.rowIsFull(row):
				self.rowCleared()
				for row2 in range(row,0,-1):
					for col in range(0,self.board.width):
						toBeReplaced = self.gameGrid.boxes[row2][col]
						toReplace = self.gameGrid.boxes[row2-1][col]
						if not (toBeReplaced.get() == toReplace.get()):
							toBeReplaced.activate()
				self.gameGrid.emptyRow(0) #Clearing the top row
		self.addTetro(Tetro.randomTetro(self.board))
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
		return self.gameGrid.getBox([dimensions[0]+Direction.colMod[d],dimensions[1]+Direction.rowMod[d]])
			
class GameGrid:
	def __init__(self,father,master=Tk()):
		self.master = master
		self.father = father
		self.boxes = [[Box(self.master,row,col) for col in range(self.father.board.width)] for row in range(self.father.board.depth)]
		for row in range(0,self.father.board.depth):
			for col in range(0,self.father.board.width):
				self.boxes[row][col].grid()
		
	def printGrid(self):
		print(str(self))
	def getBoolGrid(self):
		boolGrid = [[False for col in range(self.father.board.width)] for row in range(self.father.board.depth)]
		for row in range(0,self.father.board.depth):
			for col in range(0,self.father.board.width):
				boolGrid[row][col] = self.boxes[row][col].get()
		return boolGrid
	def __str__(self):
		boolGrid = self.getBoolGrid()
		s=""
		for row in range(0,self.father.board.depth):
			for col in range(0,self.father.board.width):
				s+=str(self.boxes[row][col])
			s+="\n"
		return s
	def rowIsFull(self,row):
		boolGrid = self.getBoolGrid()
		for col in range(0,self.father.board.width):
			if not boolGrid[row][col]: return False
		return True
	def getBox(self, dimensions):
		return self.boxes[dimensions[1]][dimensions[0]]
	def emptyRow(self, row):
		for col in range(0,self.father.board.width):
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
class Direction:
	D = "Down"
	L = "Left"
	R = "Right"
	directions = [D,L,R]
	rowMod = {D:1,L:0,R:0}
	colMod = {D:0,L:-1,R:1}
	keyCharToDirection = {'a':L,'A':L,'d':R,'D':R,'s':D,'S':D}
	