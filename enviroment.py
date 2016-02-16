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

# ******************
# *** Global Var ***
# ******************

ser = serial.Serial('/dev/cu.usbmodem1411', 115200)
time.sleep(2)
log = logging.getLogger('root')
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

    def get_reward(self):
        return ((abs(self.angle)-300)**2)/50
        
    def read_serial(self):
        line = ser.readline()
        if line[0] == 'A':
            return False
        elif line[0] == 'S':
            line = int(line[2:])
            if not line == "":
                self.angle = line // 10000
                v = line % 1000
                if v > 500:
                    self.speed = -(1000 - v)
                else:
                    self.speed = v
            return True

    def get_state(self):
        ser.write("S:gs\n".encode())

        while not self.read_serial():
            log.debug('state not sent')
            pass
        state = self.angle // 30 + (self.speed * 0.2 + 20)//1 * 0.01
        return state
        # partie entiere, position (entre -10 et 10) et decimal vitesse angulaire (0 et 40)

    def take_action(self, action):
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
