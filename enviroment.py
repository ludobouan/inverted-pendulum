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
import threading
import time

# ******************
# *** Global Var ***
# ******************

ser = serial.Serial('/dev/tty.usbmodem1411', 115200)

# *******************
# ***** CLasses *****
# *******************

log = logging.getLogger('root')

class env(threading.Thread):
    """Enviroment"""
    def __init__(self, a_actions):
        threading.Thread.__init__(self)
        self.stopping=False
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

    def stop(self):
        self.stopping=True
        ser.close()

    def run(self):
        while(not self.stopping):
            self.read_serial()
            time.sleep(0.04)


# *******************
# **** Functions ****
# *******************

# ******************
# ****** Main ******
# ******************
if __name__ == "__main__":
    import time
    acts = [-20, -10, 0, 10, 20]
    e = env(acts)
    e.start()
    try:
        while True:
            #e.read_serial()
            print e.get_state()
            time.sleep(0.05)
    except KeyboardInterrupt:
        env.stop()
        ser.close() 
        exit()
