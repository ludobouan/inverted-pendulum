# *******************
# ***** Imports *****
# *******************

import serial
import socket
import time
import threading
import random

# *******************
# *****  Class  *****
# *******************
class QEnvironment():
    """ Environment """
    def __init__(self, a_log, a_simulation):
        if a_simulation == "True":
            self.simulation = True
        elif a_simulation == "False":
            self.simulation = False
        else:
            a_log.error("Error in data")
        self.log = a_log
        self.state = ""
        self.blocked = False
        if not self.simulation:
            self.connexion = self.init_serial()
        else:
            self.connexion = self.init_socket()

    def init_serial(self):
        try:
            ser = serial.Serial('COM3', 115200)
        except serial.serialutil.SerialException:
            try:
                ser = serial.Serial('/dev/cu.usbmodem1411', 115200)
            except serial.serialutil.SerialException:
                self.log.error('Can t connect to Serial Port')
            else:
                time.sleep(1)
                return ser
        else:
            time.sleep(1)
            return ser

    def init_socket(self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            soc.connect(("192.168.1.25", 8888))
        except ConnectionRefusedError:
            self.log.error("Can't connect to Blender server")
        else:
            return soc

    def send_message(self, a_value):
        if self.simulation:
            try:
                self.connexion.send(str(a_value).encode())
            except ConnectionAbortedError:
                print("Connection closed")
        else:
            self.connexion.write("{0}\n".format(a_value).encode()) 
        time.sleep(0.030)
    
    def read_message(self):
        if not self.simulation:
            answer = str(self.connexion.readline())
            return self.message_received(answer)
        else:
            try:
                answer = self.connexion.recv(100)
                return self.message_received(answer)
            except ConnectionAbortedError:
                print("Connection closed")
                time.sleep(2)
                self.connexion = self.init_socket()

    def message_received(self, a_value):
        try:
            if self.simulation:
                a_value = str(a_value)[2:-1]
            else:
                a_value = str(a_value)[2:-5]
            if a_value[0] == "D":
                self.log.debug(a_value[2:])
                return self.read_message()

            elif a_value[0] == "I":
                self.log.info(a_value[2:])
                return self.read_message()

            elif a_value[0] == "A":
                return False

            elif a_value[0] == "S":
                self.state = a_value[2:]
                return True 
            else:
                self.log.error("Message not recognized : " + str(a_value))
        except IndexError:
            print("Connection Lost")

    def take_action(self, a_action):
        self.send_message(a_action)
        if self.blocked == True:
            try:
                while self.read_message():
                    pass
            except:
                pass

    def get_state(self):
        self.send_message("S:gs")
        try:
            while not self.read_message():
                pass
            return self.state
        except:
            pass

    def lock_message(self, a_value):
        if not self.simulation:
            if a_value:
                self.send_message("L:T")
                self.blocked = True
            else:
                self.send_message("L:F")
                self.blocked = False

    def init_episode(self):
        self.send_message("E:R")

    def close_socket(self):
        self.connexion.close()