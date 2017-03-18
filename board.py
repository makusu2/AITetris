import random
class Board:
	def __init__(self,depth=20,width=10):
		self.depth = depth
		self.width = width
		self.tetroStartPoint=(self.width/2,0)
class Tetro:#"Tetronimo" is the name of the combination of four blocks
	types = ["J","L","O","T","S","Z","I"]
	def __init__(self, type, board):
		self.type = type #Type can be J,L,O,T,S,Z,I
		self.board = board
		self.spaces = self.getStartBoxPointList()#This will change upon movement
		#Should the tetro hold a list of the dimensions of every box in it?
		
	@staticmethod
	def randomType():
		return random.choice(Tetro.types)
	@staticmethod
	def randomTetro(board):
		return Tetro(Tetro.randomType(),board)
		
	def getStartBoxPointList(self): #start is the placement of the highest block (or leftmost highest)
		start = self.board.tetroStartPoint
		if self.type == "J":
			return [[start[0],start[1]],[start[0],start[1]+1],[start[0]+1,start[1]+1],[start[0]+2,start[1]+1]]
		if self.type == "L":
			return [[start[0],start[1]],[start[0],start[1]+1],[start[0]-1,start[1]+1],[start[0]-2,start[1]+1]]
		if self.type == "O":
			return [[start[0],start[1]],[start[0]+1,start[1]],[start[0],start[1]+1],[start[0]+1,start[1]+1]]
		if self.type == "T":
			return [[start[0],start[1]],[start[0],start[1]+1],[start[0]-1,start[1]+1],[start[0]+1,start[1]+1]]
		if self.type == "S":
			return [[start[0],start[1]],[start[0]+1,start[1]],[start[0],start[1]+1],[start[0]-1,start[1]+1]]
		if self.type == "Z":
			return [[start[0],start[1]],[start[0]+1,start[1]],[start[0],start[1]+1],[start[0]-1,start[1]+1]]
		if self.type == "I":
			return [[start[0],start[1]],[start[0]+1,start[1]],[start[0]+2,start[1]],[start[0]+3,start[1]]]
		print "LETTER MATCHES NO KNOWN SHAPE!"