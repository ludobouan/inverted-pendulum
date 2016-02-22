# ********************************
# @author     : Ludovic Bouan
# @contact    : ludo.bouan@gmail.com
# created on  : 09.12.1015
# title       : 
# to do       :
# ********************************

# *******************
# ***** Imports *****
# *******************
import logging
import serial
import time
import os
import math

# ******************
# *** Global Var ***
# ******************

log = logging.getLogger('root')
ser_connected = True
try:
    ser = serial.Serial('COM3', 115200) # COM3 ou /dev/cu.usbmodem1411
except serial.serialutil.SerialException:
    log.error("Aduino not connected")
    ser_connected = False
log.info("Initialisation de la connexion Serial")
time.sleep(3)

# *******************
# ***** CLasses *****
# *******************

class env():
    """Enviroment"""
    def __init__(self):
        # super().__init__()
        self.angle = 0
        self.speed = 0
        self.state = self.get_state()
        self.reward = self.get_reward()
        fichier = open("angle.txt", "r")
        self.angles = fichier.read().split()
        fichier.close()
        fichier = open("speed.txt", "r")
        self.speeds = fichier.read().split()
        fichier.close()

    def get_reward(self):
        return (math.cos((angle*math.pi)/300)-1 + math.exp(-25*(((angle*math.pi)/300)**2)))

    def read_serial(self):
        if ser_connected:
            line = str(ser.readline())
            if line[2] == 'A':
                return False
            elif line[2] == 'S':
                line = int(line[4:len(line)-5])
                if not line == "":
                    self.angle = line // 10000
                    v = line % 1000
                    if v > 500:
                        self.speed = -(1000 - v)
                    else:
                        self.speed = v
                    if self.speed < 0:
                        self.angle += 1
                return True
            elif line[2] == 'D':
                log.debug(line[4:len(line)-5])
                return self.read_serial()
            elif line[2] == 'I':
                log.info(line[4:len(line)-5])
                return self.read_serial()
            else:
                log.debug("Error in message : " + str(line[4:len(line)-5]))
    
    def getAngle(a_angle):
        for el in self.angles:
            line = el.split(':')
            if a_angle > int(line[0]) and a_angle < int(line[1]):
                return int(line[2]), bool(line[3])
        log.error("Angle out of range")
        return 0, False
        
    def getSpeed(a_speed):
        for el in self.speeds:
            line = el.split(':')
            if a_speed > int(line[0]) and a_speed < int(line[1]):
                return int(line[2])
        log.error("Speed out of range")

    def get_state(self):
        if ser_connected:
            ser.write("S:gs\n".encode())

            while not self.read_serial():
                log.debug('State not sent')
                pass
            angle, isUpper = self.getAngle(self.angle)
            speed = self.getSpeed(self.speed)
            state = "(" + str(angle) + ", " + str(speed) + ")"
            return state, isUpper

    def take_action(self, action):
        if ser_connected:
            ser.write("{0}\n".format(action).encode())

# *******************
# **** Functions ****
# *******************

# ******************
# ****** Main ******
# ******************
if __name__ == "__main__":
    env = env()
    i = 0
    while i < 100:
        env.take_action(30)
        while env.read_serial():
            pass
        i += 1
