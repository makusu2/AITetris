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
			#print "in the additions"
			return True
		return self.parent.parent.gameGrid[tuple(index)]
		#return self.boolGrid[tuple(index)]
	def __setitem__(self,index,value):
		if not (value==True):
			print "TRYING TO SET AS NOT TRUE"
		if not index in self.boolGridAdditions:
			self.boolGridAdditions.append(tuple(index))
	def getPossibleEndStates(self,onlyBest=False):
		#print onlyBest
		#print "111"
		def isTerminalState(state):
			for box in state.tetroBoxList:
				if (box[1]+1)>=boardDepth or state[(box[0],box[1]+1)]:
					return True
			return False
		def isTerminalBoxes(state,boxes): #Might be wrong
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
			
		topBoxes = tuple([tuple(box) for box in self.tetroBoxList])
		initialDownPush = getInitialDownPush(topBoxes,self)
		startBoxes = makuUtil.sortCoords(tuple([(box[0],box[1]+initialDownPush) for box in self.tetroBoxList]))
		startState = State(startBoxes,self.parent)#!!!
		frontier = deque([tuple(startBoxes)])
		explored = {startBoxes:tuple([Directions.D]*initialDownPush)} #dict to actions
		#print "explored: ",explored
		startSorted = makuUtil.sortCoords(startBoxes)
		boxesToState = {startBoxes:startState}#!!!
		terminalStates = []
		bestTerminalVal = 0
		while frontier:
			front = frontier.popleft()
			#frontState = boxesToState[front]#!!!
			oldActions = list(explored[front])
			#newActions = frontState.getLegalActions()
			newActions = getLegalActionsBoxes(startState,front)
			#print "newActions: ",newActions
			for newAction in newActions:
				#newState = frontState.generateSuccessor(newAction)
				#newBoxes = tuple([tuple(box) for box in newState.tetroBoxList])
				#frontCoords = [tuple(box) for box in front]
				newBoxes = None
				if newAction in Directions.rotations:
					newBoxes = makuUtil.sortCoords(makuUtil.getRotatedCoords(startState,front))
				else:
					newBoxes = makuUtil.sortCoords([tuple(makuUtil.getCoordToDirection(coord,newAction)) for coord in front])#([tuple(makuUtil.getCoordToDirection(coord,newAction)) for coord in frontCoords])
				#sortedNewBoxes = makuUtil.sortCoords(newBoxes)
				#print "newBoxes: ",newBoxes
				#print "explored: ",explored
				if not newBoxes in explored.keys():
					#print "they aren't"
					#print "\nnewBoxes: ",newBoxes
					#print "\nexplored: ",explored
					#print "\noldActions: ",oldActions
					#print "\nnewAction: ",newAction
					#print "\ntuple: ",tuple(oldActions+[newAction])
					#print "\n\n\n"
					explored[newBoxes] = tuple(oldActions+[newAction])
					#boxesToState[newBoxes] = newState#!!!
					frontier.append(newBoxes)
					#if isTerminalState(newState):
					if isTerminalBoxes(startState,newBoxes):
						if onlyBest:
							#if not newState.didSomethingStupid():
							if not startState.didSomethingStupidBoxes(newBoxes):
								#print "yeah"
								#newVal = newState.evaluationFunction()
								newVal = 0#CHANGE THIS LATER
								if newVal>bestTerminalVal:
									bestTerminalVal = newVal
									terminalStates = []
								if newVal>=bestTerminalVal:
									newState = State(newBoxes,startState.parent, boolGridAdditions=startState.boolGridAdditions)#Could the creation of the state here be why the old eval val isn't working?
									terminalStates.append(newState)
						else:
							newState = State(newBoxes,startState.parent, boolGridAdditions=startState.boolGridAdditions)#Could the creation of the state here be why the old eval val isn't working?
							terminalStates.append(newState)
		if ((not terminalStates) and onlyBest):
			print "was zero, so redoing"
			return self.getPossibleEndStates(onlyBest=False)
		elif not terminalStates:
			print "WHAT"
		#print "lenTerminalStates: ",len(terminalStates)
		return terminalStates
	def evaluationFunction(self):
		def getComboSpot(col,row,state):
			if (col,row) in state.tetroBoxList:
				return True
			return state[col,row]
		boxes = self.tetroBoxList
		runningScore = 0.0
		for row in range(boardDepth-1,boardDepth-8,-1):#second argument could be 0, but I'm trying this for speed
			for col in range(boardWidth):
				if getComboSpot(col,row,self):
					height = float(boardDepth - row)
					runningScore+=(1/(height*2))
		runningScore+=self.parent.parent.points * boardWidth * 2
		if self.didSomethingStupid(): runningScore/=2
		for coord in self.tetroBoxList:
			if not makuUtil.coordsAreIllegal(self,(coord[0],coord[1]+1),checkStateTetro=True):
				runningScore/=2
		
		
		totalScore = self.runningVal + (runningScore/(2*(self.depth+1)))
		#print "runningScore: ",runningScore
		#print "totalScore: ",totalScore
		#if (random.choice([True,False,False,False])): totalScore = totalScore/2
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
		newState = State(newBoxes,self.parent,boolGridAdditions = self.boolGridAdditions)
		return newState
	def __str__(self):
		s = ""
		for row in range(boardDepth):
			for col in range(boardWidth):
				if (col,row) in self.tetroBoxList: #Is this list and not tuple?
					s+='T'
				elif self[col,row]:
					s+='#'
				else:
					s+='0'
			s+="\n"
		s+="Falling blocks: "+str(self.tetroBoxList)+"\n"
		s+="Additional true spaces: "+str(self.boolGridAdditions)+"\n"
		return s
	def expectimax(self):
		if self.depth >= maxDepth:
			return self.evaluationFunction()
		else:
			possibleNewTetros = [Tetro(tetro,self.parent.parent.board) for tetro in Tetro.types]
			possibleNewTurns = [self.generateNewTurn(tetro) for tetro in possibleNewTetros]
			possibleNewTurnVals = []
			for i in range(len(possibleNewTurns)):#possibleNewTurns:
				possibleNewEndStatesInNewTurn = possibleNewTurns[i].getPossibleEndStates(onlyBest=True)
				expectivalSum = 0
				expectivalCounter = 0
				for possibleNewEndStateInNewTurn in possibleNewEndStatesInNewTurn:
					possibleNewEndStateInNewTurn.depth = self.depth+1
					possibleNewEndStateInNewTurn.runningVal = self.runningVal
					expectival = possibleNewEndStateInNewTurn.expectimax()
					expectivalSum += expectival
					expectivalCounter+=1
				expectivalAvg = 0 if (expectivalCounter == 0) else float(expectivalSum)/expectivalCounter
				possibleNewTurnVals.append(expectivalAvg)
			expectivalAvg = makuUtil.avg(possibleNewTurnVals)
			return expectivalAvg
			
	def generateNewTurn(self,tetro):
		boolGridAdditions = self.boolGridAdditions + [tuple(coord) for coord in self.tetroBoxList]
		newCoords = copy.copy(tetro.spaces)
		newDepth = self.depth+1 #GET RID OF THIS; UNNECESSARY
		newTurnState = State(newCoords,self.parent,depth=newDepth,boolGridAdditions = boolGridAdditions)
		return newTurnState
	def didSomethingStupid(self):
		#print "1"
		#This is for checking for stuff like blocking spaces
		#TRY TO ONLY CHECK FOR SPACES NEXT TO THE TETRO
		def getImportantCoords(state):
			minCol = state.tetroBoxList[0][0]#This should work thanks to the sorting
			maxCol = state.tetroBoxList[3][0]#Same reason as above
			rows = [coord[1] for coord in tuple(state.tetroBoxList)]
			minRow = min(rows)
			maxRow = max(rows)
			leftCol = max(0,minCol-1)
			rightCol = min(boardWidth,maxCol+2)
			topRow = max(0,minRow-1)
			botRow = min(boardDepth,maxRow+2)
			return (leftCol,rightCol,topRow,botRow)
		leftCol,rightCol,topRow,botRow = getImportantCoords(self)
		for col in range(leftCol,rightCol):
			for row in range(topRow,botRow):
				currentCoord = (col,row)
				blocked = True
				for direction in [Directions.U, Directions.L, Directions.R]:
					coordToDirection = makuUtil.getCoordToDirection(currentCoord,direction)
					if not makuUtil.coordsAreIllegal(self,coordToDirection,checkStateTetro=True):
						blocked = False
				if blocked:
					return True
		return False
	def didSomethingStupidBoxes(self,boxes):
		#print "1"
		#This is for checking for stuff like blocking spaces
		#TRY TO ONLY CHECK FOR SPACES NEXT TO THE TETRO
		def getImportantCoords(state,boxes):
			minCol = boxes[0][0]#This should work thanks to the sorting
			maxCol = boxes[3][0]#Same reason as above
			rows = [coord[1] for coord in tuple(boxes)]
			minRow = min(rows)
			maxRow = max(rows)
			leftCol = max(0,minCol-1)
			rightCol = min(boardWidth,maxCol+2)
			topRow = max(0,minRow-1)
			botRow = min(boardDepth,maxRow+2)
			return (leftCol,rightCol,topRow,botRow)
		leftCol,rightCol,topRow,botRow = getImportantCoords(self,boxes)
		for col in range(leftCol,rightCol):
			for row in range(topRow,botRow):
				currentCoord = (col,row)
				blocked = True
				for direction in [Directions.U, Directions.L, Directions.R]:
					coordToDirection = makuUtil.getCoordToDirection(currentCoord,direction)
					if not makuUtil.coordsAreIllegal(self,coordToDirection,checkStateTetro=False,extraCoords=boxes):
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
		initialDownPush = getInitialDownPush(topBoxes,startState)
		startBoxes = tuple([(box[0],box[1]+initialDownPush) for box in startState.tetroBoxList])
		startState = State(startBoxes,startState.parent,startState.boolGridAdditions)
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
	endState.didSomethingStupid()
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