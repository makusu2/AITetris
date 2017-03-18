#This is for testing short bits of code without having to change directories
import Tkinter
from Tkinter import *

class Test:
	def __init__(self):
		master=Tk()
		self.check = [None,None]
		chevas = []
		for index in range(0,2):
			print "hi"
			#self.checkVar = IntVar()
			chevas.append(IntVar())
			newVa = chevas[len(chevas)-1]
			self.check[index] = Checkbutton(master,variable=newVa)
			self.check[index].grid(row=0,column=index)
			self.check[index].var = newVa
		Button(master,text="PrintIt",command=self.printIt).grid(row=1,column=0)
		mainloop()
	def printIt(self):
		print "0: ",self.check[0].var.get()
		print "1: ",self.check[1].var.get()
t = Test()
print "hi"