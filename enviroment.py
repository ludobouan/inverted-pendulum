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

    def get_reward(self):
        return ((abs(self.angle)-300)**2)/50
        
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

    def get_state(self):
        if ser_connected:
            ser.write("S:gs\n".encode())

            while not self.read_serial():
                log.debug('State not sent')
                pass
            state = self.angle // 30 + (self.speed * 0.2 + 20)//1 * 0.01
            return state
            # partie entiere, position (entre -10 et 10) et decimal vitesse angulaire (0 et 40)

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
