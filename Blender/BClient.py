import socket
import bge
import math
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 1234))

scene = bge.logic.getCurrentScene()
objList = scene.objects
pole = objList.get("pole", "Object not found")
cart = objList.get("body", "Object not found")
base = objList.get("base", "Object not found")

print("---------- Blender RL Server ----------")

try:
	while True:
		s.listen(5)
		client, address = s.accept()
		answer = client.recv(255)
		print(answer)
		if answer != "":
			if answer == "S:gs":
				print("Get state")
			else:
				print("Take action")
except KeyboardInterrupt:
	print("Program ended correctly")