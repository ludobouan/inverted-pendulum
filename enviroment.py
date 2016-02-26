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
        self.angle = 0
        self.speed = 0
        fichier = open("angle.txt", "r")
        self.angles = fichier.read().split()
        fichier.close()
        fichier = open("speed.txt", "r")
        self.speeds = fichier.read().split()
        fichier.close()
        self.state = self.get_state()[0]

    def get_reward(self):
        return (math.cos((self.angle*math.pi)/300)-1 + math.exp(-25*(((self.angle*math.pi)/300)**2)))
        #return math.cos((self.angle + 3 * self.speed)*math.pi/300)
        
    def read_serial(self):
        if ser_connected:
            line = str(ser.readline())

            # Motor done turning
            if line[0] == 'A':
                return False

            # State variables
            elif line[0] == 'S':
                line = int(line[2:])
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

            elif line[0] == 'D':
                log.debug(line[2:])
                return self.read_serial()

            elif line[0] == 'I':
                log.info(line[2:])
                return self.read_serial()

            else:
                log.debug("Error in message : " + str(line[4:len(line)-5]))
                
    def getAngle(self, a_angle):
        for el in self.angles:
            line = el.split(':')
            if a_angle >= int(line[0]) and a_angle < int(line[1]):
                return int(line[2]), self.str_to_bool(line[3])
        log.error("Angle out of range : " + str(a_angle))
        return 0, False
        
    def getSpeed(self, a_speed):
        for el in self.speeds:
            line = el.split(':')
            if a_speed >= int(line[0]) and a_speed < int(line[1]):
                return int(line[2])
        log.error("Speed out of range")

    def str_to_bool(self, a_str):
        if a_str == "True":
            return True
        if a_str == "False":
            return False

    def get_state(self):
        if ser_connected:
            ser.write("S:gs\n".encode())

            while not self.read_serial():
                log.debug('State not sent')
                pass
            angle, isUpper = self.getAngle(self.angle)
            speed = self.getSpeed(self.speed)
            state = angle + 0.01 * speed
            return state, isUpper
            

    def take_action(self, action):
        if ser_connected:
            ser.write("{0}\n".format(action).encode())