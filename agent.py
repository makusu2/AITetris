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
from collections import deque

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
	def __init__(self,boolGrid,tetroBoxList,parent,depth=0):
		self.boolGrid = boolGrid #This is a dict
		self.tetroBoxList = tetroBoxList
		self.parent = parent
		self.depth = depth
	def __getitem__(self,index):
		return self.boolGrid[tuple(index)]
	def getPossibleEndStates(self,depth=0):
		#print "1"
		def isTerminalState(state):
			for box in state.tetroBoxList:
				if (box[1]+1)>=boardDepth or state[(box[0],box[1]+1)]:
					return True
			return False
		topBoxes = tuple([tuple(box) for box in self.tetroBoxList])
		initialDownPush = getInitialDownPush(topBoxes,self.boolGrid)
		startBoxes = tuple([(box[0],box[1]+initialDownPush) for box in self.tetroBoxList])
		startState = State(self.boolGrid,startBoxes,self.parent)
		frontier = deque([startBoxes])
		explored = {startBoxes:tuple([Directions.D]*initialDownPush)} #dict to actions
		sortedExplored = [sort(startBoxes)]
		tempState = State(self.boolGrid,startBoxes,self.parent)
		boxesToState = {startBoxes:startState}
		terminalStates = []
		while frontier:
			front = frontier.popleft()
			frontState = boxesToState[front]
			oldActions = list(explored[front])
			newActions = frontState.getLegalActions()
			for newAction in newActions:
				newState = frontState.generateSuccessor(newAction)
				newBoxes = tuple([tuple(box) for box in newState.tetroBoxList])
				if not newBoxes in sortedExplored:
					explored[newBoxes] = tuple(oldActions+[newAction])
					sortedExplored.append(sort(newBoxes))
					boxesToState[newBoxes] = newState
					frontier.append(newBoxes)
					if isTerminalState(newState):
						terminalStates.append(newState)
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
					runningScore+=(1/(height*2))
		runningScore+=self.parent.parent.points * boardWidth * 2
		return runningScore
	def getLegalActions(self):
		originalActions = [d for d in Directions.legalMoves]
		actions = [d for d in Directions.legalMoves]
		for direction in originalActions:
			if direction in Directions.rotations:
				rotatedBoxes = makuUtil.getRotatedCoords(self.boolGrid,self.tetroBoxList)
				if not rotatedBoxes:
					actions.remove(direction)
					continue
				for newBox in rotatedBoxes:
					if makuUtil.coordsAreIllegal(self.boolGrid,newBox):
						if direction in actions:
							actions.remove(direction)
							continue
			else:
				for box in self.tetroBoxList:
					newBox = (box[0]+Directions.colMod[direction],box[1]+Directions.rowMod[direction])
					if makuUtil.coordsAreIllegal(self.boolGrid,newBox):
						if direction in actions:
							actions.remove(direction)
							continue
		return actions
			
	def generateSuccessor(self,direction):
		newBoolGrid = copy.copy(self.boolGrid)
		newBoxes = []
		if direction in Directions.directions:
			newBoxes = [[box[0]+Directions.colMod[direction],box[1]+Directions.rowMod[direction]] for box in self.tetroBoxList]
		elif direction in Directions.rotations:
			newBoxes = makuUtil.getRotatedCoords(self.boolGrid,self.tetroBoxList)
		newState = State(newBoolGrid,newBoxes,self.parent)
		return newState
	def __str__(self):
		s = ""
		for row in range(boardDepth):
			for col in range(boardWidth):
				if [col,row] in self.tetroBoxList: #Is this list and not tuple?
					s+='T'
				elif self[col,row]:
					s+='#'
				else:
					s+='0'
			s+="\n"
		return s
	def expectimax(self):
		if self.depth >= maxDepth:
			return self.evaluationFunction()
		else:
			possibleNewTetros = [Tetro(tetro,self.parent.parent.board) for tetro in Tetro.types]
			possibleNewTurns = [self.generateNewTurn(tetro) for tetro in possibleNewTetros]
			possibleNewTurnVals = []
			for i in range(len(possibleNewTurns)):#possibleNewTurns:
				possibleNewEndStatesInNewTurn = possibleNewTurns[i].getPossibleEndStates()
				bestNewEndStatesInNewTurn = [possibleNewEndStateInNewTurn for possibleNewEndStateInNewTurn in possibleNewEndStatesInNewTurn if not possibleNewEndStateInNewTurn.didSomethingStupid()]#[possibleNewEndStatesInNewTurn[i] for i in range(len(possibleNewEndStatesInNewTurn)) if evalVals[i]==bestEvalVal]
				expectivalSum = 0
				expectivalCounter = 0
				for possibleNewEndStateInNewTurn in bestNewEndStatesInNewTurn:
					possibleNewEndStateInNewTurn.depth = self.depth+1
					expectival = possibleNewEndStateInNewTurn.expectimax()
					expectivalSum += expectival
					expectivalCounter+=1
				expectivalAvg = 0 if (expectivalCounter == 0) else float(expectivalSum)/expectivalCounter
				possibleNewTurnVals.append(expectivalAvg)
			expectivalAvg = makuUtil.avg(possibleNewTurnVals)
			return expectivalAvg
			
	def generateNewTurn(self,tetro):
		newBoolGrid = self.generateEndTurnBoolGrid()
		newCoords = copy.copy(tetro.spaces)
		newDepth = self.depth+1
		newTurnState = State(newBoolGrid,newCoords,self.parent,depth=newDepth)
		return newTurnState
	def generateEndTurnBoolGrid(self):
		newBoolGrid = copy.copy(self.boolGrid)
		for coord in self.tetroBoxList:
			newBoolGrid[tuple(coord)] = True
		return newBoolGrid
	def didSomethingStupid(self):
		#This is for checking for stuff like blocking spaces
		def getSmallerBoolGrid(state):
			comboGrid = state.getComboGrid()
			highestGridRow = 19
			for row in range(boardDepth-1,0,-1):
				for col in range(boardWidth):
					if comboGrid[col,row]:
						highestGridRow = row
			smallerGrid = {(col,row-highestGridRow):bool(comboGrid[col,row]) for col in range(boardWidth) for row in range(highestGridRow,boardDepth)}
			return smallerGrid
		smallerGrid = getSmallerBoolGrid(self)
		gridDepth = max([coord[1] for coord in smallerGrid])+1
		gridWidth = boardWidth
		for row in range(gridDepth):
			for col in range(gridWidth):
				currentCoord = (col,row)
				blocked = True
				for direction in [Directions.U,Directions.L,Directions.R]:
					coordToDirection = makuUtil.getCoordToDirection(currentCoord,direction)
					if not makuUtil.coordsAreIllegal(smallerGrid,coordToDirection):
						blocked = False
				if blocked:
					return True
		return False
		
class Agent(Input):
	def __init__(self, parent):
		self.parent = parent
		self.grid = self.parent.gameGrid.asDict()
		self.state = None
	def newTurn(self):
		self.grid = self.parent.gameGrid.asDict()
		self.state = State(self.parent.gameGrid.asDict(),self.parent.fallingBlocks,self)
		actionsToTake = self.getActions()
		time.sleep(0.1)
		for action in actionsToTake:
			time.sleep(0.01)
			self.parent.pressedKeyChar(action)
			time.sleep(0.01)
	def getActions(self):
		#Call when a new tetro is added
		#This should return a list of actions (directions) to get the tetro to a good place
		startState = State(self.parent.gameGrid.asDict(),self.parent.fallingBlocks,self)
		possibleEndStates = startState.getPossibleEndStates()
		possibleEndStateVals = [possibleEndState.expectimax() for possibleEndState in possibleEndStates]
		bestVal = max(possibleEndStateVals)
		bestEndStates = [possibleEndStates[i] for i in range(len(possibleEndStates)) if (possibleEndStateVals[i]==bestVal)]
		endState = random.choice(bestEndStates)
		path = getPath(startState,endState)
		return path
			
		
		
		
		
def getPath(startState,endState):
	def checkPath(startState,endState,actions):
		tempState = startState
		for action in actions:
			tempState = tempState.generateSuccessor(action)
		tempStateBoxCheck = tuple([tuple(box) for box in tempState.tetroBoxList])
		endStateBoxCheck = tuple([tuple(box) for box in endState.tetroBoxList])
		if tempStateBoxCheck == endStateBoxCheck:
			return tuple(list(actions)+[Directions.D])
		else:
			print "temp: ",tempStateBoxCheck
			print "end: ",endStateBoxCheck
	def pathFinder(startState,endState):
		topBoxes = tuple([tuple(box) for box in startState.tetroBoxList])
		initialDownPush = getInitialDownPush(topBoxes,startState.boolGrid)
		startBoxes = tuple([(box[0],box[1]+initialDownPush) for box in startState.tetroBoxList])
		startState = State(startState.boolGrid,startBoxes,startState.parent)
		frontier = deque([startBoxes])
		explored = {startBoxes:tuple([Directions.D]*initialDownPush)} #dict to actions
		debDict = {startBoxes:(startBoxes)}
		tempState = State(startState.boolGrid,startBoxes,startState.parent)
		boxesToState = {startBoxes:startState}
		terminalStates = []
		testEndBoxes = tuple([tuple(box) for box in endState.tetroBoxList])
		while frontier:
			front = frontier.popleft()
			frontState = boxesToState[front]
			oldActions = list(explored[front])
			newActions = frontState.getLegalActions()
			for newAction in newActions:
				newState = frontState.generateSuccessor(newAction)
				newBoxes = tuple([tuple(box) for box in newState.tetroBoxList])
				if not newBoxes in explored:
					explored[newBoxes] = tuple(oldActions+[newAction])
					debDict[newBoxes] = tuple(list(debDict[front])+[newBoxes])
					boxesToState[newBoxes] = newState
					if newBoxes == testEndBoxes:
						pathActions = tuple(list(explored[front])+[newAction])
						return pathActions
					frontier.append(newBoxes)
	pathFound = pathFinder(startState,endState)
	endState.didSomethingStupid()
	return checkPath(startState,endState,pathFound)
def getInitialDownPush(startBoxes,boolGrid):
	deepestBoxRow = max([box[1] for box in startBoxes])
	highestGridRow = 19
	for row in range(boardDepth-1,0,-1):
		for col in range(boardWidth):
			if boolGrid[col,row]:
				highestGridRow = row
	calculatedDownPush = highestGridRow-deepestBoxRow-1
	return max(0,calculatedDownPush)