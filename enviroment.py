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
import os
import DbManager
import logging
import sys
import serial

# ******************
# *** Global Var ***
# ******************

ser = serial.Serial('COM3', 115200)

# *******************
# ***** CLasses *****
# *******************

log = logging.getLogger('root')

class env():
    """Enviroment"""
    def __init__(self, a_actions):
        # super().__init__()
        self.angle = 0
        self.speed = 0
        self.state = self.get_state()
        self.reward = self.get_reward()

    def get_reward(self):
        return ((abs(self.angle)-300)**2)/50
        
    def read_serial(self):
        line = ser.readline()
        line = int(line)
        if not line == "":
            self.angle = line // 10000
            v = line % 1000
            if v > 500:
                self.speed = -(1000 - v)
            else:
                self.speed = v

    def get_state(self):
        self.read_serial()
        state = self.angle // 30 + (self.speed * 0.2 + 20)//1 * 0.01
        return state
        # partie entiere, position (entre -10 et 10) et decimal vitesse angulaire (0 et 40)

    def take_action(self, value):
        ser.write("{0}\n".format(value).encode())


# *******************
# **** Functions ****
# *******************

# ******************
# ****** Main ******
# ******************
if __name__ == "__main__":
    pass