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

# ******************
# *** Global Var ***
# ******************

# *******************
# ***** CLasses *****
# *******************

class env:
    """Enviroment"""
    def __init__(self, a_actions):
        # super().__init__()
        self.angle = get_angle()
        self.speed = get_speed()
        self.state = get_state()
        self.reward = get_reward()

    def get_reward(self):
        return(-self.angle^2)

    def get_angle(self):
        pass

    def get_speed(self):
        pass

    def get_state(self):


# *******************
# **** Functions ****
# *******************

# ******************
# ****** Main ******
# ******************
if __name__ == "__main__":
    pass