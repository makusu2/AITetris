#So, this will be just an addition method of input, I think. Also, maybe this can hold both the agents AND the keyboard input.
import display
#from display import Direction
import Tkinter
from Tkinter import *
from board import *
import time
import copy
import makuUtil
from makuUtil import *
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
		#self.tetroBoxList = QuadCoords(tetroBoxList)
		self.tetroBoxList = tetroBoxList
		self.parent = parent
		self.depth = depth
		self.runningVal = runningVal
	def __getitem__(self,index): #Doesn't include tetro
		if index in self.tetroBoxList:
			return False
		return (index in self.boolGridAdditions) or self.parent.parent.gameGrid[tuple(index)]
	def __setitem__(self,index,value):
		if not (value==True):
			print "TRYING TO SET AS NOT TRUE"
		if not index in self.boolGridAdditions:
			self.boolGridAdditions.append(tuple(index))
			
	def getPossibleEndStates(self,onlyBest=False):
		def isTerminalBoxes(state,boxes):
			#print "boxes: ",boxes
			for box in boxes:
				if (box[1]+1)>=boardDepth or state[(box[0],box[1]+1)]:
					return True
			return False
		def newStateCoords(coords,state):
			return State(coords,self.parent,boolGridAdditions=state.boolGridAdditions,runningVal=state.runningVal,depth=state.depth)
		def getLegalActionsBoxes(state,boxes):
			originalActions = [d for d in Directions.legalMoves]
			actions = [d for d in Directions.legalMoves]
			for direction in originalActions:
				if direction in Directions.rotations:
					rotatedBoxes = boxes.rotatedCoords(state)
					if not rotatedBoxes:
						actions.remove(direction)
						continue
					if rotatedBoxes.hasIllegalCoords(state) and (direction in actions):
						actions.remove(direction)
						continue
				else:
					newBoxes = boxes.pushedToDirectionCoords(direction)
					if newBoxes.hasIllegalCoords(state) and (direction in actions):
						actions.remove(direction)
						continue
			return actions
		initialDownPush = getInitialDownPush(self.tetroBoxList,self)
		startBoxes = self.tetroBoxList.pushedDownCoords(initialDownPush)
		startState = State(startBoxes,self.parent,depth=self.depth,runningVal=self.runningVal)
		frontier = deque([startBoxes])
		explored = {startBoxes:tuple([Directions.D]*initialDownPush)} #dict to actions
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
					newBoxes =front.rotatedCoords(startState)
				else:
					newBoxes = front.pushedToDirectionCoords(newAction)
				if not newBoxes in explored:
					explored[newBoxes] = tuple(oldActions+[newAction])
					frontier.append(newBoxes)
					if isTerminalBoxes(startState,newBoxes):
						if not onlyBest:
							newState = newStateCoords(newBoxes,startState)
							terminalStates.append(newState)
						elif not startState.didSomethingStupidBoxes(newBoxes):
							newShortVal = newBoxes.evaluationFunction()
							if newShortVal>bestShortTerminalVal:
								newState = newStateCoords(newBoxes,startState)
								terminalStates=[newState]
								bestTerminalVal = newState.evaluationFunction()
								bestShortTerminalVal=newShortVal
							elif newShortVal==bestShortTerminalVal:
								newState = newStateCoords(newBoxes,startState)
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
		#print "depth: ",self.depth
		def getComboSpot(col,row,state):
			if (col,row) in state.tetroBoxList:
				return True
			return state[col,row]
		boxes = self.tetroBoxList
		runningScore = 0.0
		runningScore+=self.tetroBoxList.evaluationFunction()
		runningScore+=self.parent.parent.points * boardWidth * 2
		
		testScore = runningScore
		for box in self.tetroBoxList:
			boxDown = makuUtil.getCoordToDirection(box,Directions.D)
			while not makuUtil.coordsAreIllegal(self,boxDown,checkStateTetro=True):
				runningScore-=1
				boxDown = makuUtil.getCoordToDirection(boxDown,Directions.D)
			boxUp = makuUtil.getCoordToDirection(box,Directions.U)
			if makuUtil.coordsAreIllegal(self,boxUp,checkStateTetro=False):
				runningScore+=3
			for direction in [Directions.L,Directions.R]:
				sideBox = makuUtil.getCoordToDirection(box,direction)
				if makuUtil.coordsAreIllegal(self,(sideBox[0],sideBox[1]),checkStateTetro=False):
					runningScore+=0.8
		topRow = self.tetroBoxList.topRow
		if topRow<(boardDepth/2): runningScore-=10
		elif topRow<5: runningScore-=50
		elif topRow<2: runningScore-=500
		if self.didSomethingStupidBoxes(self.tetroBoxList): runningScore=runningScore-abs(runningScore/2)
		if self.depth==0: return runningScore
		return self.runningVal+(runningScore/(2*((self.depth+1))))
		
		
		
	def getLegalActions(self):
		originalActions = [d for d in Directions.legalMoves]
		actions = [d for d in Directions.legalMoves]
		for direction in originalActions:
			if direction in Directions.rotations:
				rotatedBoxes = self.tetroBoxList.rotatedCoords(self)
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
			newBoxes = self.tetroBoxList.rotatedCoords(self)
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
		s+="Coord eval func: "+str(self.tetroBoxList.evaluationFunction())+"\n"
		s+="Did something stupid: "+str(self.didSomethingStupidBoxes(self.tetroBoxList))+"\n"
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
				bestVal = max([state.expectimax() for state in possibleNewEndStatesInNewTurn])
				possibleNewTurnVals.append(bestVal)
			expectivalAvg = makuUtil.avg(possibleNewTurnVals)
			return self.evaluationFunction()+expectivalAvg
			
	def generateNewTurn(self,tetro):
		boolGridAdditions = self.boolGridAdditions + [tuple(coord) for coord in self.tetroBoxList]
		newCoords = copy.copy(tetro.spaces)
		newTurnState = State(newCoords,self.parent,boolGridAdditions = boolGridAdditions,runningVal=self.runningVal,depth=self.depth+1)
		return newTurnState
	def didSomethingStupidBoxes(self,boxes):
		for col in range(boxes.leftCol-1,boxes.rightCol+2):
			for row in range(boxes.topRow-1,boxes.botRow+2):
				currentCoord = (col,row)
				if makuUtil.coordsAreIllegal(self,currentCoord,checkStateTetro=False,extraCoords=boxes): continue
				blocked = True
				for direction in [Directions.U, Directions.L, Directions.R]:
					coordToDirection = makuUtil.getCoordToDirection(currentCoord,direction)
					if not makuUtil.coordsAreIllegal(self,coordToDirection,checkStateTetro=False,extraCoords=boxes):
						blocked = False
				if blocked:
					return True
		return False
	def createNextDepth(self, coords):
		return State(coords,self.parent,boolGridAdditions=self.boolGridAdditions,runningVal=self.runningVal,depth=self.depth+1)
class Agent(Input):
	def __init__(self, parent):
		self.parent = parent
	def __getitem__(self,index):
		return self.parent[index]
	def newTurn(self):
		startCoords = QuadCoords(tuple([tuple(block) for block in self.parent.fallingBlocks]))
		actionsToTake = self.getActions()
		time.sleep(0.01)
		for action in actionsToTake:
			time.sleep(0.1)
			self.parent.pressedKeyChar(action)
			time.sleep(0.1)
	def getActions(self):
		#Call when a new tetro is added
		#This should return a list of actions (directions) to get the tetro to a good place
		startState = State(self.parent.fallingBlocks,self)
		#print "StartState depth: ",startState.depth
		possibleEndStates = startState.getPossibleEndStates()
		#print "firstEndDepth: ",possibleEndStates[0].depth
		possibleEndStateVals = [possibleEndState.expectimax() for possibleEndState in possibleEndStates] #CAN BE EXPECTIMAX OR EVAL FUNC
		bestVal = max(possibleEndStateVals)
		bestEndStates = [possibleEndStates[i] for i in range(len(possibleEndStates)) if (possibleEndStateVals[i]==bestVal)]
		endState = random.choice(bestEndStates)
		path = getPath(startState,endState)
		return path
			
		
		
		
		
def getPath(startState,endState):
	#def checkPath(startState,endState,actions):
		#print "startState: ",startState
		#print "endState: ",endState
		#tempState = startState
		#for action in actions:
		#	tempState = tempState.generateSuccessor(action)
		#tempStateBoxCheck = tuple([tuple(box) for box in tempState.tetroBoxList])
		#endStateBoxCheck = tuple([tuple(box) for box in endState.tetroBoxList])
		#if tempStateBoxCheck == endStateBoxCheck:
		#	return tuple(list(actions)+[Directions.D])
		#else:
		#	print "temp: ",tempStateBoxCheck
		#	print "end: ",endStateBoxCheck
		
		
		
	def pathFinder(startState,endState):
		def getLegalActionsBoxes(state,boxes):
			originalActions = [d for d in Directions.legalMoves]
			actions = [d for d in Directions.legalMoves]
			for direction in originalActions:
				if direction in Directions.rotations:
					rotatedBoxes = boxes.rotatedCoords(state)
					if not rotatedBoxes:
						actions.remove(direction)
						continue
					if rotatedBoxes.hasIllegalCoords(state) and (direction in actions):
						actions.remove(direction)
						continue
				else:
					newBoxes = boxes.pushedToDirectionCoords(direction)
					if newBoxes.hasIllegalCoords(state) and (direction in actions):
						actions.remove(direction)
						continue
			return actions
		def isTerminalBoxes(state,boxes):
			for box in boxes:
				if (box[1]+1)>=boardDepth or state[(box[0],box[1]+1)]:
					return True
			return False
		topBoxes = startState.tetroBoxList
		initialDownPush = getInitialDownPush(topBoxes,startState)
		startBoxes = startState.tetroBoxList.pushedDownCoords(initialDownPush)
		startState = State(startBoxes,startState.parent,boolGridAdditions=startState.boolGridAdditions)
		frontier = deque([startBoxes])
		explored = {startBoxes:tuple([Directions.D]*initialDownPush)} #dict to actions
		terminalStates = []
		testEndBoxes = endState.tetroBoxList
		while frontier:
			front = frontier.popleft()
			oldActions = list(explored[front])
			newActions = getLegalActionsBoxes(startState,front)
			for newAction in newActions:
				newBoxes = front.rotatedCoords(startState) if (newAction in Directions.rotations) else front.pushedToDirectionCoords(newAction)
				if not newBoxes in explored:
					explored[newBoxes] = tuple(oldActions+[newAction])
					if newBoxes == testEndBoxes:
						pathActions = tuple(list(explored[front])+[newAction])
						return pathActions
					frontier.append(newBoxes)
	pathFound = pathFinder(startState,endState)
	#approvedPath = checkPath(startState,endState,pathFound)
	return tuple(list(pathFound)+[Directions.D])
	
	
	
	
	
def getInitialDownPush(startBoxes,state):
	highestGridRow = 19
	for row in range(boardDepth-1,0,-1):
		for col in range(boardWidth):
			if state[col,row]:
				highestGridRow = row
	calculatedDownPush = highestGridRow-startBoxes.botRow-1
	return max(0,calculatedDownPush)