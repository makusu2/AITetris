import pyscreenshot as ImageGrab
import time
start_Time = time.time()
times = [x for x in range(1,10)]
current_Time = time.time()
while(current_Time - start_Time < 10):
	current_Time = time.time()
	if (current_Time - start_Time) in times:
		im = ImageGrab.grab()
		im.show()
