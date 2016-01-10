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

class env():
    """Enviroment"""
    def __init__(self, a_actions):
        # super().__init__()
        self.angle = get_angle()
        self.speed = get_speed()
        self.state = get_state()
        self.reward = get_reward()
        while true:
            self.read_serial()

    def get_reward(self):
        return(-self.angle^2)
        
    def read_serial(self):
        line = ser.readline()
        if not line == "":
            self.angle = line // 10000
            self.speed = line % 1000

    def get_state(self):
        return self.angle / 30 + (self.speed * 0.2 + 20) / 100
        # partie entiere, position (entre -10 et 10) et decimal vitesse angulaire (0 et 40)

    def take_action(self, value):
        ser.write(value+"\n")


# *******************
# **** Functions ****
# *******************

# ******************
# ****** Main ******
# ******************
if __name__ == "__main__":
    pass