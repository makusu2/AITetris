#So, this will be just an addition method of input, I think. Also, maybe this can hold both the agents AND the keyboard input.
import display
#from display import Direction
import Tkinter
from Tkinter import *
from board import *
import time
import copy
import makuUtil
from makuUtil import Directions
import conf
from conf import *
import random
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

class State:
	def __init__(self,boolGrid,tetroBoxList,parent):
		#boolGrid is without the starting tetro
		self.boolGrid = boolGrid #This is a dict
		self.tetroBoxList = tetroBoxList
		self.parent = parent
	def getPossibleEndStates(self):
		def getPossibleTetrosAtBottom():
			tetroBoxCols = [dim[0] for dim in self.tetroBoxList]
			tetroBoxRows = [dim[1] for dim in self.tetroBoxList]
			leftMostCol,rightMostCol = (min(tetroBoxCols),max(tetroBoxCols))
			#rightMostCol = max(tetroBoxCols)
			downMostRow = max(tetroBoxRows)
			tetroWidth = 1+rightMostCol-leftMostCol
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
		possibleEndTetros = []
		bottomTetros = getPossibleTetrosAtBottom()
		for bottomTetro in bottomTetros:
			uncovered = False
			while not uncovered:
				uncovered = True
				for bottomTetroBox in bottomTetro:
					bottomTetroTuple = tuple(bottomTetroBox)
					if self.boolGrid[bottomTetroTuple]:
						uncovered = False
				if not uncovered:
					for i in range(0,len(bottomTetro)):
						currentBox = bottomTetro[i]
						bottomTetro[i] = [currentBox[0],currentBox[1]-1]
			possibleEndTetros.append(bottomTetro)
		possibleEndStates = [State(self.boolGrid,possibleEndTetro,self.parent) for possibleEndTetro in possibleEndTetros]
		return possibleEndStates#States
	def getPossibleEndStates2(self):
		def isTerminalState(state):
			for box in state.tetroBoxList:
				if (box[1]+1)>=boardDepth or state.boolGrid[(box[0],box[1]+1)]:
				#	print "first"
					#print "terminal state: \n",str(state)
					#print "terminal state score: ",state.evaluationFunction()
					return True
				#elif state.boolGrid[(box[0],box[1]+1)]:
				#	print "second"
				#	return True
			return False
		#So, frontier should be list of box locations instead
		startBoxes = tuple([tuple(box) for box in self.tetroBoxList])
		frontier = [startBoxes]
		explored = {startBoxes:tuple()}
		boxesToState = {startBoxes:self}
		terminalStates = []
		while frontier:
			#print "frontier: ",frontier
			front = frontier.pop()
			#print "Front: ",front
			frontState = boxesToState[front]
			#print "frontState: \n",frontState
			oldActions = list(explored[front])
			#print "oldActions: ",oldActions
			newActions = frontState.getLegalActions()
			#print "newActions: ",newActions
			for newAction in newActions:
				#print " newAction: ",newAction
				newState = frontState.generateSuccessor(newAction)
				#print " newState: \n",str(newState)
				newBoxes = tuple([tuple(box) for box in newState.tetroBoxList])
				if not newBoxes in explored:
					explored[newBoxes] = tuple(oldActions+[newAction])
					boxesToState[newBoxes] = newState
					frontier.append(newBoxes)
					if isTerminalState(newState):
						terminalStates.append(newState)
			#time.sleep(1)
		#time.sleep(5)
		#terminalStrings = [str(ts) for ts in terminalStates]
		#for ts in terminalStrings:
		#	print ts
		#	print "\n\n"
		#print "terminalStates: ",terminalStates
		#print "\n\n\n\n\n\n\n\n"
		return terminalStates
	def getComboGrid(self):
		comboGrid = copy.copy(self.boolGrid)
		for tetroBox in self.tetroBoxList:
			comboGrid[tuple(tetroBox)] = True
		return comboGrid
	def evaluationFunction(self):
		boxes = self.tetroBoxList
		comboGrid = self.getComboGrid()
		runningScore = 0.0
		for row in range(boardDepth-1,0,-1):
			for col in range(boardWidth):
				if comboGrid[(col,row)]:
					height = float(boardDepth - row)
					runningScore+=(1/height)
		#print "score: ",runningScore
		return runningScore
	def getLegalActions(self):
		actions = copy.copy(Directions.directions)
		for direction in Directions.directions:
			for box in self.tetroBoxList:
				newBox = (box[0]+Directions.colMod[direction],box[1]+Directions.rowMod[direction])
				newBoxIllegal = ((newBox[1]<0) | (newBox[0]<0) | (newBox[0]>=boardWidth) | (newBox[1]>=boardDepth))
				if newBoxIllegal or self.boolGrid[newBox]:
					#if self.boolGrid[tuple(box)]:
					#	print "THAT'S WHY!NOI@NOIN!O"
					if direction in actions:
						actions.remove(direction)
				#newBoxBreaksRules = ((newBox[1]<0) | (newBox[0]<0) | (newBox[0]>=boardWidth) | (self.boolGrid[newBox]))
				#if newBoxBreaksRules:
				#	actions.remove(direction)
		#print "legalActions: ",actions
		return actions
	def generateSuccessor(self,direction):
		newBoolGrid = copy.copy(self.boolGrid)
		newBoxes = [[box[0]+Directions.colMod[direction],box[1]+Directions.rowMod[direction]] for box in self.tetroBoxList]
		newState = State(newBoolGrid,newBoxes,self.parent)
		return newState
	def __str__(self):
		s = ""
		for row in range(boardDepth):
			for col in range(boardWidth):
				if [col,row] in self.tetroBoxList: #Is this list and not tuple?
					s+='T'
				elif self.boolGrid[(col,row)]:
					s+='#'
				else:
					s+='0'
			s+="\n"
		return s
		
class Agent(Input):
	def __init__(self, parent):
		self.parent = parent
		self.grid = parent.gameGrid.getBoolGrid()
		self.state = None
	def newTurn(self):
		self.grid = self.parent.gameGrid.getBoolGrid()
		self.state = State(self.grid,self.parent.fallingTetro.getStartBoxPointList,self)
		actionsToTake = self.getActions()
		for action in actionsToTake:
			time.sleep(0.01)
			self.parent.pressedKeyChar(action)
			time.sleep(0.01)
	def getActions(self):
		#Call when a new tetro is added
		#This should return a list of actions (directions) to get the tetro to a good place
		startState = self.getStartState()
		endState = self.getEndState(startState)
		#startPos = startState
		path = getPath(startState,endState)
		return path#indexing since both should now be coordinates
	def getBoolListWithoutTetro(self):
		boolGridDict = self.parent.gameGrid.asDict()
		tetroList = self.parent.fallingTetro.getStartBoxPointList()
		for tetroSpot in tetroList:
			boolGridDict[tuple(tetroSpot)] = False
		return boolGridDict
	def getStartState(self):
		tetroList = self.parent.fallingTetro.getStartBoxPointList()
		startState = State(self.getBoolListWithoutTetro,tetroList,self)
		return startState
	def getEndState(self,startState):
		state = State(self.getBoolListWithoutTetro(),self.parent.fallingTetro.getStartBoxPointList(),self)
		#endStatesToVals = dict([(endState,self.evaluationFunction(endState)) for endState in state.getPossibleEndStates()])
		possibleEndStates = state.getPossibleEndStates2()
		state.getPossibleEndStates2()
		possibleEndStateVals = [possibleEndState.evaluationFunction() for possibleEndState in possibleEndStates]
		bestVal = max(possibleEndStateVals)
		bestEndStates = [possibleEndStates[i] for i in range(len(possibleEndStates)) if (possibleEndStateVals[i]==bestVal)]
		return random.choice(bestEndStates)
		
		
		
		
		
def getPath(startState,endState):
		startCol,startRow = startState.tetroBoxList[0]
		endCol,endRow = endState.tetroBoxList[0]
		actions = []
		horDiff,vertDiff = (startCol-endCol,startRow-endRow)
		horKey = Directions.L if (horDiff>0) else Directions.R
		verKey = Directions.D
		for i in range(abs(horDiff)): actions.append(horKey)
		for i in range(abs(vertDiff)+1): actions.append(verKey)
		return actions
		