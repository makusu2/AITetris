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
		#boolGrid is without the starting tetro
		#print "creating state with depth of ",depth
		self.boolGrid = boolGrid #This is a dict
		self.tetroBoxList = tetroBoxList
		self.parent = parent
		self.depth = depth
	def __getitem__(self,index):
		return self.boolGrid[tuple(index)]
	def getPossibleEndStates(self,depth=0):
		def isTerminalState(state):
			for box in state.tetroBoxList:
				if (box[1]+1)>=boardDepth or state[(box[0],box[1]+1)]:
					return True
			return False
		#So, frontier should be list of box locations instead
		startBoxes = tuple([tuple(box) for box in self.tetroBoxList])
		frontier = deque([startBoxes])
		explored = {startBoxes:tuple()}
		boxesToState = {startBoxes:self}
		terminalStates = []
		while frontier:
			#print "1"
			front = frontier.popleft()
			#print "2"
			frontState = boxesToState[front]
			#print "3"
			oldActions = list(explored[front])
			#print "4"
			newActions = frontState.getLegalActions()
			#print "5"
			for newAction in newActions:
				newState = frontState.generateSuccessor(newAction)
				newBoxes = tuple([tuple(box) for box in newState.tetroBoxList])
				if not newBoxes in explored:
					explored[newBoxes] = tuple(oldActions+[newAction])
					boxesToState[newBoxes] = newState
					frontier.append(newBoxes)
					if isTerminalState(newState):
						terminalStates.append(newState)
		#print "finished"
		return terminalStates
	def getComboGrid(self):
		comboGrid = copy.copy(self.boolGrid)
		for tetroBox in self.tetroBoxList:
			comboGrid[tuple(tetroBox)] = True
		return comboGrid
	def evaluationFunction(self):
		#print "eval1"
		boxes = self.tetroBoxList
		comboGrid = self.getComboGrid()
		runningScore = 0.0
		for row in range(boardDepth-1,0,-1):
			for col in range(boardWidth):
				if comboGrid[(col,row)]:
					height = float(boardDepth - row)
					runningScore+=(1/height)
		#print "eval2"
		runningScore+=self.parent.parent.points * boardWidth * 2
		return runningScore
	def getLegalActions(self):
		#print "boolGrid: ",self.boolGrid
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
					#print "direction: ",direction
					#print "newBox: ",newBox
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
		#print self
		#print "depth: ",self.depth
		#maybe increment depth here?
		if self.depth >= maxDepth:
			#print "yep"
			return self.evaluationFunction()
		else:
			possibleNewTetros = [Tetro(tetro,self.parent.parent.board) for tetro in Tetro.types]
			#print "nope"
			possibleNewTurns = [self.generateNewTurn(tetro) for tetro in possibleNewTetros]
			#print "1"
			#print "lenPossibleNewTurns: ",len(possibleNewTurns)
			possibleNewTurnVals = []
			for possibleNewTurn in possibleNewTurns:
				possibleNewEndStatesInNewTurn = possibleNewTurn.getPossibleEndStates()
				expectivalSum = 0
				expectivalCounter = 0
				for possibleNewEndStateInNewTurn in possibleNewEndStatesInNewTurn:
					possibleNewEndStateInNewTurn.depth = self.depth+1
					expectival = possibleNewEndStateInNewTurn.expectimax()
					expectivalSum += expectival
					expectivalCounter+=1
				expectivalAvg = 0 if (expectivalCounter == 0) else float(expectivalSum)/expectivalCounter
				possibleNewTurnVals.append(expectivalAvg)
			expectivalAvg = makuUtil.avg(possibleNewTurnVals)
			return expectivalAvg
				
			#possibleNewEndStates = [turn.getPossibleEndStates(depth=self.depth+1) for turn in possibleNewTurns]
			#for possibleNewEndState in possibleNewEndStates:
			#	if not possibleNewEndState:
			#		return 0 #means something fukd up
			##print "len possibleNewEndStates: ",len(possibleNewEndStates)
			#print "len possibleNewEndStates[0]: ",len(possibleNewEndStates[0])
			#print "2"
			#should we use expectimax instead in the next line?
			#if not possibleNewEndStates:
			#	return 0 #Dunno why we have to do this
			#for possibleNewEndState in possibleNewEndStates:
			#	expectiVals = [successorState.expectimax() for successorState in possibleNewEndState
			possibleNewEndStatesVals = [[state.expectimax() for state in states] for states in possibleNewEndStates]
			#print "possibleNewEndStatesVals: ",possibleNewEndStatesVals
			#if not possibleNewEndStatesVals:
			#	return 0 #Dunno why we have to do this
			bestNewEndStatesVals = [max(vals) for vals in possibleNewEndStatesVals]
			#if not bestNewEndStatesVals:
			#	return 0 #Dunno why we have to do this
			avgVal = float(sum(bestNewEndStatesVals))/len(bestNewEndStatesVals)
			return avgVal
			#possibleNewStatesAvgVals = [(float(sum(vals))/len(vals)) for vals in possibleNewEndStateVals]
			#bestEndStates = [
			#possibleNewVals = [possibleNewTurn.expectimaxVal() for possibleNewTurn in possibleNewTurns]
			#avgVal = float(sum(possibleNewVals))/len(possibleNewVals
			#return avgVal
			
	def generateNewTurn(self,tetro):
		newBoolGrid = self.generateEndTurnBoolGrid()
		newCoords = copy.copy(tetro.spaces)
		newDepth = self.depth+1
		#print "newDepth: ",newDepth
		newTurnState = State(newBoolGrid,newCoords,self.parent,depth=newDepth)
		return newTurnState
	def generateEndTurnBoolGrid(self):
		newBoolGrid = copy.copy(self.boolGrid)
		for coord in self.tetroBoxList:
			newBoolGrid[tuple(coord)] = True
		return newBoolGrid
		
class Agent(Input):
	def __init__(self, parent):
		self.parent = parent
		self.grid = self.parent.gameGrid.asDict()#parent.gameGrid.getBoolGrid()
		self.state = None
	def newTurn(self):
		self.grid = self.parent.gameGrid.asDict()#self.parent.gameGrid.getBoolGrid()
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
		#Next could be eval func
		possibleEndStateVals = [possibleEndState.expectimax() for possibleEndState in possibleEndStates]
		bestVal = max(possibleEndStateVals)
		bestEndStates = [possibleEndStates[i] for i in range(len(possibleEndStates)) if (possibleEndStateVals[i]==bestVal)]
		endState = random.choice(bestEndStates)
		path = getPath(startState,endState)
		return path
		
		
		
		
def getPath(startState,endState):
	startBoxes = tuple([tuple(box) for box in startState.tetroBoxList])
	frontier = deque([startBoxes])
	explored = {startBoxes:()} #dict to actions
	boxesToState = {startBoxes:startState}
	terminalStates = []
	while frontier:
		front = frontier.popleft()
		frontState = boxesToState[front]
		if front == tuple([tuple(box) for box in endState.tetroBoxList]):
			return tuple(list(explored[front])+[Directions.D])
		oldActions = list(explored[front])
		newActions = frontState.getLegalActions()
		for newAction in newActions:
			newState = frontState.generateSuccessor(newAction)
			newBoxes = tuple([tuple(box) for box in newState.tetroBoxList])
			if not newBoxes in explored:
				explored[newBoxes] = tuple(oldActions+[newAction])
				boxesToState[newBoxes] = newState
				frontier.append(newBoxes)