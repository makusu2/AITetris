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
import math
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
	def __init__(self,tetroBoxList,parent,depth=0,runningVal=0,boolGridAdditions=[]):
		self.boolGridAdditions = boolGridAdditions
		self.tetroBoxList = makuUtil.sortCoords(tetroBoxList)
		self.parent = parent
		self.depth = depth
		self.runningVal = runningVal
	def __getitem__(self,index): #Doesn't include tetro
		if index in self.tetroBoxList:
			return False
		if index in self.boolGridAdditions: 
			return True
		return self.parent.parent.gameGrid[tuple(index)]
		#return self.boolGrid[tuple(index)]
	def __setitem__(self,index,value):
		if not (value==True):
			print "TRYING TO SET AS NOT TRUE"
		if not index in self.boolGridAdditions:
			self.boolGridAdditions.append(tuple(index))
	def getPossibleEndStates(self,onlyBest=False):
		def isTerminalBoxes(state,boxes):
			for box in boxes:
				if (box[1]+1)>=boardDepth or state[(box[0],box[1]+1)]:
					return True
			return False
		def getLegalActionsBoxes(state,boxes):
			originalActions = [d for d in Directions.legalMoves]
			actions = [d for d in Directions.legalMoves]
			for direction in originalActions:
				if direction in Directions.rotations:
					rotatedBoxes = makuUtil.getRotatedCoords(state,boxes)
					if not rotatedBoxes:
						actions.remove(direction)
						continue
					for newBox in rotatedBoxes:
						if makuUtil.coordsAreIllegal(state,newBox):
							if direction in actions:
								actions.remove(direction)
								continue
				else:
					for box in boxes:
						newBox = (box[0]+Directions.colMod[direction],box[1]+Directions.rowMod[direction])
						if makuUtil.coordsAreIllegal(state,newBox):
							if direction in actions:
								actions.remove(direction)
								continue
			return actions
		initialDownPush = getInitialDownPush(self.tetroBoxList,self)
		startBoxes = makuUtil.sortCoords(tuple([(box[0],box[1]+initialDownPush) for box in self.tetroBoxList]))
		startState = State(startBoxes,self.parent,depth=self.depth,runningVal=self.runningVal)
		frontier = deque([tuple(startBoxes)])
		explored = {startBoxes:tuple([Directions.D]*initialDownPush)} #dict to actions
		startSorted = makuUtil.sortCoords(startBoxes)
		terminalStates = []
		bestShortTerminalVal = 0
		bestTerminalVal = 0 #SHOULD USE COORD VALUES
		while frontier:
			front = frontier.popleft()
			oldActions = list(explored[front])
			newActions = getLegalActionsBoxes(startState,front)
			for newAction in newActions:
				newBoxes = None
				if newAction in Directions.rotations:
					newBoxes = makuUtil.getRotatedCoords(startState,front)
				else:
					newBoxes = makuUtil.sortCoords([tuple(makuUtil.getCoordToDirection(coord,newAction)) for coord in front])
				if not newBoxes in explored:
					explored[newBoxes] = tuple(oldActions+[newAction])
					frontier.append(newBoxes)
					if isTerminalBoxes(startState,newBoxes):
						if not onlyBest:
							newState = startState.createNextDepth(newBoxes)#State(newBoxes,startState.parent, boolGridAdditions=startState.boolGridAdditions,runningVal=self.runningVal,depth=self.depth+1)
							terminalStates.append(newState)
						elif not startState.didSomethingStupidBoxes(newBoxes):
							newShortVal = coordEvaluationFunction(newBoxes)
							if newShortVal>bestShortTerminalVal:
								newState = startState.createNextDepth(newBoxes)#State(newBoxes,startState.parent, boolGridAdditions=startState.boolGridAdditions,runningVal=self.runningVal,depth=self.depth+1)
								terminalStates=[newState]
								bestTerminalVal = newState.evaluationFunction()
								bestShortTerminalVal=newShortVal
							elif newShortVal==bestShortTerminalVal:
								newState = startState.createNextDepth(newBoxes)#State(newBoxes,startState.parent, boolGridAdditions=startState.boolGridAdditions,runningVal=self.runningVal,depth=self.depth+1)
								newVal = newState.evaluationFunction()
								if newVal>bestTerminalVal:
									terminalStates = [newState]
									bestTerminalVal = newVal
								elif newVal==bestTerminalVal:
									terminalStates.append(newState)
		if ((not terminalStates) and onlyBest):
			print "was zero, so redoing"
			return self.getPossibleEndStates(onlyBest=False)
		elif not terminalStates: print "WHAT"
		return terminalStates
		
	def evaluationFunction(self):
		def getComboSpot(col,row,state):
			if (col,row) in state.tetroBoxList:
				return True
			return state[col,row]
		boxes = self.tetroBoxList
		runningScore = 0.0
		runningScore+=coordEvaluationFunction(self.tetroBoxList)
		runningScore+=self.parent.parent.points * boardWidth * 2
		for box in self.tetroBoxList:
			boxDown = makuUtil.getCoordToDirection(box,Directions.D)
			while not makuUtil.coordsAreIllegal(self,boxDown,checkStateTetro=True):
				runningScore-=0.3
				boxDown = makuUtil.getCoordToDirection(boxDown,Directions.D)
			boxUp = makuUtil.getCoordToDirection(box,Directions.U)
			if makuUtil.coordsAreIllegal(self,boxUp,checkStateTetro=False):
				runningScore+=3
			for direction in [Directions.L,Directions.R]:
				sideBox = makuUtil.getCoordToDirection(box,direction)
				if not makuUtil.coordsAreIllegal(self,(sideBox[0],sideBox[1]),checkStateTetro=True):
					runningScore-=0.25
		if self.didSomethingStupidBoxes(self.tetroBoxList): runningScore/=4
		if self.depth==0:
			return runningScore
		totalScore = self.runningVal+(runningScore/(self.depth+1))
		return totalScore
	def getLegalActions(self):
		originalActions = [d for d in Directions.legalMoves]
		actions = [d for d in Directions.legalMoves]
		for direction in originalActions:
			if direction in Directions.rotations:
				rotatedBoxes = makuUtil.getRotatedCoords(self,self.tetroBoxList)
				if not rotatedBoxes:
					actions.remove(direction)
					continue
				for newBox in rotatedBoxes:
					if makuUtil.coordsAreIllegal(self,newBox):
						if direction in actions:
							actions.remove(direction)
							continue
			else:
				for box in self.tetroBoxList:
					newBox = (box[0]+Directions.colMod[direction],box[1]+Directions.rowMod[direction])
					if makuUtil.coordsAreIllegal(self,newBox):
						if direction in actions:
							actions.remove(direction)
							continue
		return actions
			
	def generateSuccessor(self,direction):
		newBoxes = []
		if direction in Directions.directions:
			newBoxes = [[box[0]+Directions.colMod[direction],box[1]+Directions.rowMod[direction]] for box in self.tetroBoxList]
		elif direction in Directions.rotations:
			newBoxes = makuUtil.getRotatedCoords(self,self.tetroBoxList)
		newState = State(newBoxes,self.parent,depth=self.depth,boolGridAdditions = self.boolGridAdditions)
		return newState
	def __str__(self):
		s = "\n"
		for row in range(boardDepth):
			for col in range(boardWidth):
				if (col,row) in self.tetroBoxList:
					s+='T'
				elif self[col,row]:
					s+='#'
				else:
					s+='0'
			s+="\n"
		s+="Falling blocks: "+str(self.tetroBoxList)+"\n"
		s+="Additional true spaces: "+str(self.boolGridAdditions)+"\n"
		s+="Depth: "+str(self.depth)+"\n"
		s+="Running score: "+str(self.runningVal)+"\n"
		s+="Evaluation function: "+str(self.evaluationFunction())+"\n"
		s+="Coord eval func: "+str(coordEvaluationFunction(self.tetroBoxList))+"\n"
		return s
	def expectimax(self):
		if self.depth >= maxDepth:
			return self.evaluationFunction()
		else:
			possibleNewTetros = [Tetro(tetro,self.parent.parent.board) for tetro in Tetro.types]
			possibleNewTurns = [self.generateNewTurn(tetro) for tetro in possibleNewTetros]
			#Can we just create one possible new turn, and change the tetro instead?
			possibleNewTurnVals = []
			for i in range(len(possibleNewTurns)):#possibleNewTurns:
				possibleNewEndStatesInNewTurn = possibleNewTurns[i].getPossibleEndStates(onlyBest=False)
				expectivalSum = 0
				expectivalCounter = 0
				for possibleNewEndStateInNewTurn in possibleNewEndStatesInNewTurn:
					#possibleNewEndStateInNewTurn.depth = self.depth+1
					#possibleNewEndStateInNewTurn.runningVal = self.runningVal
					expectival = possibleNewEndStateInNewTurn.expectimax()
					expectivalSum += expectival
					expectivalCounter+=1
				expectivalAvg = 0 if (expectivalCounter == 0) else float(expectivalSum)/expectivalCounter
				possibleNewTurnVals.append(expectivalAvg)
			expectivalAvg = makuUtil.avg(possibleNewTurnVals)
			#print "avg: ",expectivalAvg
			return expectivalAvg
			
	def generateNewTurn(self,tetro):
		boolGridAdditions = self.boolGridAdditions + [tuple(coord) for coord in self.tetroBoxList]
		newCoords = copy.copy(tetro.spaces)
		newTurnState = State(newCoords,self.parent,boolGridAdditions = boolGridAdditions,runningVal=self.runningVal,depth=self.depth)
		return newTurnState
	def didSomethingStupidBoxes(self,boxes):
		#print "1"
		#This is for checking for stuff like blocking spaces
		#TRY TO ONLY CHECK FOR SPACES NEXT TO THE TETRO
		#return False #CHANGE THIS LATER!!!
		def getImportantCoords(state,boxes):
			minCol = boxes[0][0]#This should work thanks to the sorting
			maxCol = boxes[3][0]#Same reason as above
			rows = [coord[1] for coord in tuple(boxes)]
			minRow = min(rows)
			maxRow = max(rows)
			leftCol = max(0,minCol-1)
			rightCol = min(boardWidth,maxCol+2)
			topRow = max(0,minRow-1)#was 1
			botRow = min(boardDepth,maxRow+2) #was 2
			return (leftCol,rightCol,topRow,botRow)
		leftCol,rightCol,topRow,botRow = getImportantCoords(self,boxes)
		for col in range(leftCol,rightCol):
			for row in range(topRow,botRow):
				currentCoord = (col,row)
				if currentCoord in boxes: continue
				blocked = True
				for direction in [Directions.U, Directions.L, Directions.R]:
					coordToDirection = makuUtil.getCoordToDirection(currentCoord,direction)
					#print "boxes1: ",boxes
					if not makuUtil.coordsAreIllegal(self,coordToDirection,checkStateTetro=False,extraCoords=boxes):
						#print "extraCoords: ",boxes
						blocked = False
					#print "boxes2: ",boxes
				if blocked:
					#print "1112"
					return True
		return False
	def createNextDepth(self, coords):
		newState = State(coords,self.parent,boolGridAdditions=self.boolGridAdditions,runningVal=self.runningVal,depth=self.depth+1)
		return newState
class Agent(Input):
	def __init__(self, parent):
		self.parent = parent
		self.grid = self.parent.gameGrid.asDict()
		self.state = None
	def newTurn(self):
		self.grid = self.parent.gameGrid.asDict()
		startCoords = tuple([tuple(block) for block in self.parent.fallingBlocks])
		self.state = State(startCoords,self)
		actionsToTake = self.getActions()
		time.sleep(0.1)
		for action in actionsToTake:
			time.sleep(0.01)
			self.parent.pressedKeyChar(action)
			time.sleep(0.01)
	def getActions(self):
		#Call when a new tetro is added
		#This should return a list of actions (directions) to get the tetro to a good place
		startState = State(self.parent.fallingBlocks,self)
		possibleEndStates = startState.getPossibleEndStates()
		possibleEndStateVals = [possibleEndState.evaluationFunction() for possibleEndState in possibleEndStates] #CAN BE EXPECTIMAX OR EVAL FUNC
		#for i in range(len(possibleEndStates)):
		#	print "state: ",possibleEndStates[i]
		#	time.sleep(1)
		bestVal = max(possibleEndStateVals)
		bestEndStates = [possibleEndStates[i] for i in range(len(possibleEndStates)) if (possibleEndStateVals[i]==bestVal)]
		endState = random.choice(bestEndStates)
		path = getPath(startState,endState)
		return path
			
		
		
		
		
def getPath(startState,endState):
	def checkPath(startState,endState,actions):
		#print "startState: ",startState
		#print "endState: ",endState
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
		initialDownPush = getInitialDownPush(topBoxes,startState)
		startBoxes = tuple([(box[0],box[1]+initialDownPush) for box in startState.tetroBoxList])
		startState = State(startBoxes,startState.parent,boolGridAdditions=startState.boolGridAdditions)
		frontier = deque([startBoxes])
		explored = {startBoxes:tuple([Directions.D]*initialDownPush)} #dict to actions
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
					boxesToState[newBoxes] = newState
					if newBoxes == testEndBoxes:
						pathActions = tuple(list(explored[front])+[newAction])
						return pathActions
					frontier.append(newBoxes)
	pathFound = pathFinder(startState,endState)
	approvedPath = checkPath(startState,endState,pathFound)
	return approvedPath
def getInitialDownPush(startBoxes,state):
	deepestBoxRow = max([box[1] for box in startBoxes])
	highestGridRow = 19
	for row in range(boardDepth-1,0,-1):
		for col in range(boardWidth):
			if state[col,row]:
				highestGridRow = row
	calculatedDownPush = highestGridRow-deepestBoxRow-1
	return max(0,calculatedDownPush)
def magStatesStr(numStates):
	mag = int(math.log10(numStates))
	return mag
def coordEvaluationFunction(coords):
	#print "coords: ",coords
	val = sum([coord[1] for coord in coords])
	return val