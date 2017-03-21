#So, this will be just an addition method of input, I think. Also, maybe this can hold both the agents AND the keyboard input.
import display
#from display import Direction
import Tkinter
from Tkinter import *
from board import *
import time
import copy
class Input:
	def __init__(self, parent):
		self.parent = parent
class KeyboardInput(Input):
	def __init__(self, parent):
		self.parent = parent
		self.master = Tk()
		self.master.title("Tetris")
		self.master.geometry("300x300")
		Label(self.master, text = "Play Tetris!\n\n").pack()
		Label(self.master,text="Click here for keyboard input").pack()
		self.master.bind("<Key>",self.pressedKey)
	def pressedKey(self,key):
		self.parent.pressedKey(key)
	def newTurn(self):
		print "New turn started"#this is only used in agent
class AgentState:
	def __init__(self,boolGrid,tetroBoxList,parent):
		#boolGrid is without the starting tetro
		self.boolGrid = boolGrid #I think this is a list of coordinates
		self.tetroBoxList = tetroBoxList
		self.parent = parent
	def getPossibleEndStates(self):
		def getPossibleTetrosAtBottom():
			tetroBoxCols = [dim[0] for dim in self.tetroBoxList]
			tetroBoxRows = [dim[1] for dim in self.tetroBoxList]
			leftMostCol = min(tetroBoxCols)
			rightMostCol = max(tetroBoxCols)
			downMostRow = max(tetroBoxRows)
			tetroWidth = 1+rightMostCol-leftMostCol
			boardDepth = self.parent.parent.board.depth
			boardWidth = self.parent.parent.board.width
			downPush = (boardDepth-downMostRow)-1
			leftMostDownPlacements = [[tetroBox[0]-leftMostCol,tetroBox[1]+downPush] for tetroBox in self.tetroBoxList]
			rightMostPush = boardWidth-tetroWidth
			tetrosAtBottom = []
			for rightPush in range(0,rightMostPush):
				currentTetroBoxes = []
				for box in leftMostDownPlacements:
					currentTetroBoxes.append([box[0]+rightPush,box[1]])
				tetrosAtBottom.append(currentTetroBoxes)
			return tetrosAtBottom
		#First, get the tetro list if it were at the bottom of the map, even overlapping
		possibleEndStates = []
		bottomTetros = getPossibleTetrosAtBottom()
		for bottomTetro in bottomTetros:
			weGood = False
			while not weGood:
				weGood = True
				for bottomTetroBox in bottomTetro:
					bottomTetroTuple = tuple(bottomTetroBox)
					if self.boolGrid[bottomTetroTuple]:
						weGood = False
				if not weGood:
					for i in range(0,len(bottomTetro)):
						currentBox = bottomTetro[i]
						bottomTetro[i] = [currentBox[0],currentBox[1]-1]
			possibleEndStates.append(bottomTetro)
		possibleEnds = [AgentState(self.boolGrid,possibleEndState,self.parent) for possibleEndState in possibleEndStates]
		return possibleEnds#States
		
	def getComboGrid(self):
		comboGrid = copy.copy(self.boolGrid)
		for tetroBox in self.tetroBoxList:
			comboGrid[tuple(tetroBox)] = True
		return comboGrid
		
class Agent(Input):
	def __init__(self, parent):
		self.parent = parent
		self.grid = parent.gameGrid.getBoolGrid()
		self.state = None
	def newTurn(self):
		self.grid = self.parent.gameGrid.getBoolGrid()
		self.state = AgentState(self.grid,self.parent.fallingTetro.getStartBoxPointList,self)
		actionsToTake = self.getActions()
		for action in actionsToTake:
			time.sleep(0.01)
			self.parent.agentPressedKey(action)
			time.sleep(0.01)
	def getActions(self):
		#Call when a new tetro is added
		#This should return a list of actions (directions) to get the tetro to a good place
		startState = self.getStartState()
		endState = self.getEndState(startState)
		startPos = startState
		path = getPath(startState,endState)
		return path#indexing since both should now be coordinates
	def getBoolListWithoutTetro(self):
		boolGridDict = self.parent.gameGrid.getBoolGridDict()
		tetroList = self.parent.fallingTetro.getStartBoxPointList()
		for tetroSpot in tetroList:
			boolGridDict[tuple(tetroSpot)] = False
		return boolGridDict
	def getStartState(self):
		tetroList = self.parent.fallingTetro.getStartBoxPointList()
		startState = AgentState(self.getBoolListWithoutTetro,tetroList,self)
		return startState
	def getEndState(self,startState):
		agentState = AgentState(self.getBoolListWithoutTetro(),self.parent.fallingTetro.getStartBoxPointList(),self)
		possibleEndStates = agentState.getPossibleEndStates()
		possibleEndStateVals = [self.evaluateEndState(possibleEndState) for possibleEndState in possibleEndStates]
		return possibleEndStates[possibleEndStateVals.index(max(possibleEndStateVals))]
		
		
	def evaluateEndState(self, endState):
		boxes = endState.tetroBoxList
		comboGrid = endState.getComboGrid()
		bottomRowFilledBoxes = 0
		for col in range(self.parent.board.width):
			if comboGrid[(col,self.parent.board.depth-1)]:
				bottomRowFilledBoxes+=1
		return bottomRowFilledBoxes
		numRowsFilled = len([row for row in range(self.parent.board.width) if self.parent.gameGrid.rowIsFull(row)])
		return numRowsFilled
def getPath(startState,endState):
		startCol,startRow = startState.tetroBoxList[0]
		endCol,endRow = endState.tetroBoxList[0]
		actions = []
		horDiff = startCol-endCol
		vertDiff = startRow-endRow
		horKey = "a" if (horDiff>0) else "d"
		verKey = "s"
		for i in range(abs(horDiff)): actions.append(horKey)
		for i in range(abs(vertDiff)+1): actions.append(verKey)
		return actions
		