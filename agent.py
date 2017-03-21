#So, this will be just an addition method of input, I think. Also, maybe this can hold both the agents AND the keyboard input.
import display
#from display import Direction
import Tkinter
from Tkinter import *
from board import *
import time
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
	def getStartState(self):
		return self.tetroBoxList
	def getPossibleEndStates(self):
		#First, get the tetro list if it were at the bottom of the map, even overlapping
		possibleEndStates = []
		bottomTetros = self.getPossibleTetrosAtBottom()
		#print "bottomTetros: ",bottomTetros
		#print "bottomTetros: ",bottomTetros
		for bottomTetro in bottomTetros:
			weGood = False
			while not weGood:
				weGood = True
				for bottomTetroBox in bottomTetro:
					#for bottomTetroBox in bottomTetroBoxes:
					bottomTetroTuple = tuple(bottomTetroBox)
					#print "boolGrid: ",self.boolGrid
					if self.boolGrid[bottomTetroTuple]:# in boolGrid.asList():
						weGood = False
				if not weGood:
					for i in range(0,len(bottomTetro)):
						currentBox = bottomTetro[i]
						bottomTetro[i] = [currentBox[0],currentBox[1]-1]
			possibleEndStates.append(bottomTetro)
		return possibleEndStates
		#Then, for each, move each box up until nothing overlaps
	def getPossibleTetrosAtBottom(self):
		tetroBoxCols = [dim[0] for dim in self.tetroBoxList]
		tetroBoxRows = [dim[1] for dim in self.tetroBoxList]
		leftMostCol = min(tetroBoxCols)
		rightMostCol = max(tetroBoxCols)
		downMostRow = max(tetroBoxRows)
		#print "tetroBoxList: ",self.tetroBoxList
		#print "downMostRow: ",downMostRow
		tetroWidth = 1+rightMostCol-leftMostCol
		boardDepth = self.parent.parent.board.depth
		boardWidth = self.parent.parent.board.width
		downPush = (boardDepth-downMostRow)-1#I think?
		leftMostDownPlacements = [[tetroBox[0]-leftMostCol,tetroBox[1]+downPush] for tetroBox in self.tetroBoxList]
		rightMostPush = boardWidth-tetroWidth
		tetrosAtBottom = []
		for rightPush in range(0,rightMostPush):
			currentTetroBoxes = []
			for box in leftMostDownPlacements:
				currentTetroBoxes.append([box[0]+rightPush,box[1]])
			tetrosAtBottom.append(currentTetroBoxes)
		#tetrosAtBottom = [[leftMostDownPlacements[0]+rightPush,leftMostDownPlacements[1]] for rightPush in range(0,rightMostPush)]
		return tetrosAtBottom
		
class Agent(Input):
	def __init__(self, parent):
		self.parent = parent
		self.grid = parent.gameGrid.getBoolGrid()
		self.state = None
	def newTurn(self):
		self.grid = self.parent.gameGrid.getBoolGrid()
		#print "3"
		self.state = AgentState(self.grid,self.parent.fallingTetro.getStartBoxPointList,self)
		print "1"
		actionsToTake = self.getActions()
		for action in actionsToTake:
			time.sleep(0.1)
			print "2"
			self.parent.agentPressedKey(action)
			time.sleep(0.1)
	def getActions(self):
		#Call when a new tetro is added
		#This should return a list of actions (directions) to get the tetro to a good place
		startState = self.getStartState()
		endState = self.getEndState(startState)
		startPos = startState
		return getPath(startState[0],endState[0])#.append("d")#indexing since both should now be coordinates
	#def getCost(self):
	#	print "nope"
		#Do we need this? Does Tetris really have a "cost" for the movement of tetros?
	#def getHeuristic(self):
	def getBoolListWithoutTetro(self):
		#tempGridDict = {}
		boolGridDict = self.parent.gameGrid.getBoolGridDict()
		#for boolSpot in self.grid:
		#	tempGridDict[(boolSpot[0],boolSpot[1]) = self.grid[boolSpot[0],boolSpot[1]]
		#tempGridList = [[boolSpot[0],boolSpot[1]] for boolSpot in self.grid]
		#tempGridDict = {[boolSpot[0],boolSpot[1]]:
		tetroList = self.parent.fallingTetro.getStartBoxPointList()
		for tetroSpot in tetroList:
			boolGridDict[tuple(tetroSpot)] = False
		#tempGrid = []
		
		return boolGridDict
	def getStartState(self):
		tetroList = self.parent.fallingTetro.getStartBoxPointList()
		startState = AgentState(self.getBoolListWithoutTetro,tetroList,self)
		return startState.getStartState()
	def getEndState(self,startState):
		agentState = AgentState(self.getBoolListWithoutTetro(),self.parent.fallingTetro.getStartBoxPointList(),self)
		possibleEndStates = agentState.getPossibleEndStates()
		#print "possibleEndStates: ",possibleEndStates
		#print "tetro: ",self.parent.fallingTetro
		possibleEndStateVals = [self.evaluateEndState(possibleEndState) for possibleEndState in possibleEndStates]
		return possibleEndStates[possibleEndStateVals.index(max(possibleEndStateVals))]
		
		
		#possibleStates = #getEachEndPlacement(self,startState)
		possibleStateVals = [self.evaluateEndState(endState) for endState in possibleStates]
		bestIndex = possibleStateVals.index(min(possibleStateVals))
		bestStateTemp = possibleStates[bestIndex]
		endState = AgentState(self.getBoolListWithoutTetro(),bestStateTemp,self)
		return endState
		#return possibleStates[bestIndex]
		#Could we try doing this for each of the rotations of the piece,
		#then get the best from each, then choose the best of the four rotations?
		
	def evaluateEndState(self, endState):
		numRowsFilled = len([row for row in range(self.parent.board.width) if self.parent.gameGrid.rowIsFull(row)])
		return numRowsFilled
	def getEachEndPlacement(self,startState):
		tetro = self.parent.fallingTetro
		startBoxPlaces = tetro.getStartBoxPointList
		startBoxCols = [startBoxPlace[0] for startBoxPlace in startBoxPlaces]
		leftMostBox = min(startBoxCols)
		rightMostBox = max(startBoxCols)
		boxesWidth = 1+rightMostBox-leftMostBox
		possibleEndBoxesPlacements = []
		leftMostBoxPlacements = [[startBoxPlace[0]-leftMostBox,startBoxPlace[1]] for startBoxPlace in startBoxPlaces]
		#possibleEndBoxPlacements.append(leftMostBoxPlaces)
		for rightPush in range(0,self.parent.board.width-boxesWidth):
			possibleEndBoxesPlacement = [leftMostBoxPlacements[0]+rightPush,leftMostBoxPlacements[1]]
			possibleEndBoxesPlacements.append(possibleEndBoxesPlacement)
		botBoxesList = [[possibleEndBoxesPlacement[0],possibleEndBoxesPlacement[1]+self.parent.depth-1] for possibleEndBoxesPlacement in possibleEndBoxesPlacements]
		endPlacements = []
		for botBoxes in botBoxesList:
			while True:
				if True in [self.parent.gameGrid.get(botBox) for botBox in botBoxes]:
					botBoxes = [[boxBox[0],botBox[1]+1] for botBox in botBoxes]
					continue
				else:
					endPlacements.append(botBoxes)
					break
		return endPlacements
def getPath(startState,endState):
		currentState = [startDim for startDim in startState]
		actions = []
		moveLeft = (startState[0]>endState[0])
		if moveLeft:
			while (currentState[0]>endState[0]):
				actions.append("a")
				currentState[0]=currentState[0]-1
		else:
			while (currentState[0]<endState[0]):
				actions.append("d")
				currentState[0] = currentState[0]+1
		while (currentState[1]<endState[1]):
			actions.append("s")
			currentState[1] = currentState[1]+1
		actions.append("s")
		return actions
		